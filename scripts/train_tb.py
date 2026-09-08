"""
AI Clinical Decision Support System (AI-CDSS)
State-of-the-Art (SOTA) Tuberculosis Detection Training Engine

Architecture: ConvNeXt-Tiny (Modern Pure ConvNet with 7x7 Depthwise Kernels)
Features:
- High Resolution: 384x384 with aspect-ratio preserving letterboxing
- Adaptive Medical Contrast Equalization
- PyTorch Automatic Mixed Precision (AMP fp16) for NVIDIA RTX 4060 GPU
- Focal Loss with Inverse Frequency Class Weighting & Label Smoothing
- Two-Phase Transfer Learning (Head Warmup -> Discriminative Backbone Fine-Tuning)
- Comprehensive Clinical Metrics: Sensitivity (Recall), Specificity, Macro-F1, Confusion Matrix
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Any

from PIL import Image, ImageOps
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from ai_core.models.convnext import ConvNeXtXRay
from ai_core.models.densenet import DenseNet121XRay
from ai_core.training.checkpoint import save_checkpoint

CLASS_NAMES = ["Normal", "Tuberculosis"]
CLASS_DIR_MAP = {
    "normal": 0,
    "neg": 0,
    "negative": 0,
    "tuberculosis": 1,
    "tb": 1,
    "pos": 1,
    "positive": 1
}

def letterbox_image(image: Image.Image, target_size: int = 384) -> Image.Image:
    """Preserves anatomical aspect ratio by resizing and centering on a black canvas."""
    src_w, src_h = image.size
    scale = target_size / max(src_w, src_h)
    new_w, new_h = max(1, int(src_w * scale)), max(1, int(src_h * scale))
    resized = image.resize((new_w, new_h), Image.Resampling.BILINEAR)
    
    canvas = Image.new("RGB", (target_size, target_size), (0, 0, 0))
    pad_left = (target_size - new_w) // 2
    pad_top = (target_size - new_h) // 2
    canvas.paste(resized, (pad_left, pad_top))
    return canvas

def enhance_medical_contrast(image: Image.Image) -> Image.Image:
    """Applies adaptive histogram equalization and contrast stretching."""
    gray = image.convert("L")
    eq = ImageOps.equalize(gray)
    auto = ImageOps.autocontrast(gray, cutoff=1)
    blended = Image.blend(auto, eq, alpha=0.5)
    return blended.convert("RGB")

class FocalLoss(nn.Module):
    """Focal Loss to address class imbalance and penalize hard false negatives."""
    def __init__(self, alpha=None, gamma: float = 2.0, label_smoothing: float = 0.05):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.label_smoothing = label_smoothing

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        ce_loss = F.cross_entropy(
            inputs, targets, weight=self.alpha, reduction="none", label_smoothing=self.label_smoothing
        )
        pt = torch.exp(-ce_loss)
        focal_loss = ((1.0 - pt) ** self.gamma) * ce_loss
        return focal_loss.mean()

class MedicalXRayDataset(Dataset):
    def __init__(self, samples: List[Tuple[str, int]], transform=None):
        self.samples = samples
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        image = Image.open(path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label

def scan_directory(dir_path: str) -> List[Tuple[str, int]]:
    """Scans directory for Tuberculosis and Normal images."""
    samples = []
    if not os.path.exists(dir_path):
        return samples
    
    for root, dirs, files in os.walk(dir_path):
        folder_name = os.path.basename(root).lower()
        if folder_name in CLASS_DIR_MAP:
            label = CLASS_DIR_MAP[folder_name]
            for fname in files:
                if fname.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                    samples.append((os.path.join(root, fname), label))
    return samples

def evaluate_loader(model, loader, criterion, device, desc="Evaluating"):
    model.eval()
    t_loss, all_preds, all_labels = 0.0, [], []
    eval_iter = tqdm(loader, desc=desc, leave=False) if HAS_TQDM else loader
    with torch.no_grad():
        for imgs, lbls in eval_iter:
            imgs, lbls = imgs.to(device), lbls.to(device)
            out = model(imgs)
            loss = criterion(out, lbls)
            t_loss += loss.item() * imgs.size(0)
            preds = out.argmax(dim=1).cpu().tolist()
            all_preds.extend(preds)
            all_labels.extend(lbls.cpu().tolist())

    y_true = np.array(all_labels)
    y_pred = np.array(all_preds)
    total_acc = (y_true == y_pred).mean() if len(y_true) > 0 else 0.0

    f1s = []
    for i in range(len(CLASS_NAMES)):
        tp = np.sum((y_true == i) & (y_pred == i))
        fp = np.sum((y_true != i) & (y_pred == i))
        fn = np.sum((y_true == i) & (y_pred != i))
        prec = tp / max(tp + fp, 1)
        rec = tp / max(tp + fn, 1)
        f1 = 2 * (prec * rec) / max(prec + rec, 1e-7)
        f1s.append(f1)
    macro_f1 = np.mean(f1s) if f1s else 0.0
    avg_loss = t_loss / max(len(loader.dataset), 1)
    return avg_loss, total_acc, macro_f1, y_true, y_pred

def run_training(args):
    project_root = Path(__file__).parent.parent
    data_dir = Path(args.data_dir) if args.data_dir else project_root / "data" / "raw"
    export_path = Path(args.export_path) if args.export_path else project_root / "data" / "models" / "best_model.pth"

    print("=" * 70)
    print("  AI-CDSS: SOTA Tuberculosis Detection Training Engine")
    print(f"  Backbone Architecture: {args.backbone.upper()}")
    print(f"  Target Resolution    : {args.image_size}x{args.image_size}")
    print(f"  Target Classes       : {CLASS_NAMES}")
    print("=" * 70)

    # Locate splits
    train_dir = data_dir / "train"
    val_dir = data_dir / "val" if (data_dir / "val").exists() else data_dir / "validation"
    test_dir = data_dir / "test"

    train_samples = scan_directory(str(train_dir)) if train_dir.exists() else []
    val_samples = scan_directory(str(val_dir)) if val_dir.exists() else []
    test_samples = scan_directory(str(test_dir)) if test_dir.exists() else []

    # If no pre-split folders exist, search root of data_dir and partition automatically
    if not train_samples:
        print(f"[*] No separate train/val folders found. Scanning '{data_dir}' for full dataset...")
        all_samples = scan_directory(str(data_dir))
        if not all_samples:
            print(f"\n[ERROR] No images found in {data_dir}!")
            print(f"Please place Tuberculosis dataset inside '{data_dir}' with NORMAL/ and TUBERCULOSIS/ subfolders.")
            return 1

        np.random.seed(42)
        np.random.shuffle(all_samples)
        n_total = len(all_samples)
        n_train = int(n_total * 0.8)
        n_val = int(n_total * 0.1)
        train_samples = all_samples[:n_train]
        val_samples = all_samples[n_train:n_train + n_val]
        test_samples = all_samples[n_train + n_val:]

    print(f"Dataset Partition -> Train: {len(train_samples)}, Val: {len(val_samples)}, Test: {len(test_samples)}")

    # Calculate class counts and weights
    class_counts = [0, 0]
    for _, label in train_samples:
        if label < 2:
            class_counts[label] += 1
    
    total_train = max(len(train_samples), 1)
    class_weights = [total_train / (2.0 * max(c, 1)) for c in class_counts]
    class_weights = [w / sum(class_weights) * 2.0 for w in class_weights]
    weights_tensor = torch.tensor(class_weights, dtype=torch.float32)
    print(f"Train Class Distribution: Normal={class_counts[0]}, Tuberculosis={class_counts[1]}")
    print(f"Focal Loss Inverse Class Weights: {[round(w, 3) for w in class_weights]}")

    # Transforms
    train_transform = transforms.Compose([
        transforms.Lambda(lambda img: enhance_medical_contrast(img)),
        transforms.Lambda(lambda img: letterbox_image(img, args.image_size)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomAffine(degrees=7, translate=(0.04, 0.04), scale=(0.96, 1.04)),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        transforms.RandomErasing(p=0.25, scale=(0.02, 0.12), value="random")
    ])

    eval_transform = transforms.Compose([
        transforms.Lambda(lambda img: enhance_medical_contrast(img)),
        transforms.Lambda(lambda img: letterbox_image(img, args.image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_loader = DataLoader(MedicalXRayDataset(train_samples, transform=train_transform), batch_size=args.batch_size, shuffle=True, num_workers=args.num_workers)
    val_loader = DataLoader(MedicalXRayDataset(val_samples, transform=eval_transform), batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)
    test_loader = DataLoader(MedicalXRayDataset(test_samples, transform=eval_transform), batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers) if test_samples else None

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Compute Hardware: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    # Instantiate Model
    if args.backbone == "convnext_tiny":
        model = ConvNeXtXRay(num_classes=2, pretrained=True, classes=CLASS_NAMES).to(device)
        model_name = "ConvNeXt-Tiny"
    else:
        model = DenseNet121XRay(num_classes=2, pretrained=True, classes=CLASS_NAMES).to(device)
        model_name = "DenseNet121"

    criterion = FocalLoss(alpha=weights_tensor.to(device), gamma=2.0, label_smoothing=0.05)
    scaler = torch.amp.GradScaler('cuda') if torch.cuda.is_available() else None

    best_val_f1 = -1.0

    # Phase 1: Head Warmup
    print(f"\n--- Phase 1: Classifier Head Warmup ({args.head_epochs} Epochs) ---")
    model.freeze_backbone()
    optimizer_head = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3, weight_decay=1e-4)
    scheduler_head = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer_head, T_max=max(args.head_epochs, 1))

    for epoch in range(1, args.head_epochs + 1):
        model.train()
        t_loss, correct, total = 0.0, 0, 0
        start = time.time()
        
        train_iter = tqdm(enumerate(train_loader), total=len(train_loader), desc=f"Epoch {epoch}/{args.head_epochs} [Head]", leave=True) if HAS_TQDM else enumerate(train_loader)
        for batch_idx, (imgs, lbls) in train_iter:
            imgs, lbls = imgs.to(device), lbls.to(device)
            optimizer_head.zero_grad()

            if scaler is not None:
                with torch.amp.autocast('cuda'):
                    out = model(imgs)
                    loss = criterion(out, lbls)
                scaler.scale(loss).backward()
                scaler.step(optimizer_head)
                scaler.update()
            else:
                out = model(imgs)
                loss = criterion(out, lbls)
                loss.backward()
                optimizer_head.step()

            t_loss += loss.item() * imgs.size(0)
            preds = out.argmax(dim=1)
            correct += (preds == lbls).sum().item()
            total += lbls.size(0)

        scheduler_head.step()
        elapsed = time.time() - start
        val_loss, val_acc, val_f1, _, _ = evaluate_loader(model, val_loader, criterion, device, desc=f"Epoch {epoch}/{args.head_epochs} [Val]")
        print(f"Epoch {epoch}/{args.head_epochs} [Head] - Train Loss: {t_loss/total:.4f}, Acc: {correct/total*100:.1f}% | Val Acc: {val_acc*100:.1f}%, Macro-F1: {val_f1*100:.1f}% ({elapsed:.1f}s)")

    # Phase 2: Discriminative Fine-Tuning
    print(f"\n--- Phase 2: Deep Backbone Fine-Tuning ({args.ft_epochs} Epochs) ---")
    if hasattr(model, "unfreeze_stages"):
        model.unfreeze_stages()
    else:
        model.unfreeze_all()

    optimizer_ft = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4, weight_decay=1e-4)
    scheduler_ft = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer_ft, T_max=max(args.ft_epochs, 1), eta_min=1e-6)

    for epoch in range(1, args.ft_epochs + 1):
        model.train()
        t_loss, correct, total = 0.0, 0, 0
        start = time.time()
        
        train_iter = tqdm(enumerate(train_loader), total=len(train_loader), desc=f"Epoch {epoch}/{args.ft_epochs} [Fine-Tune]", leave=True) if HAS_TQDM else enumerate(train_loader)
        for batch_idx, (imgs, lbls) in train_iter:
            imgs, lbls = imgs.to(device), lbls.to(device)
            optimizer_ft.zero_grad()

            if scaler is not None:
                with torch.amp.autocast('cuda'):
                    out = model(imgs)
                    loss = criterion(out, lbls)
                scaler.scale(loss).backward()
                scaler.step(optimizer_ft)
                scaler.update()
            else:
                out = model(imgs)
                loss = criterion(out, lbls)
                loss.backward()
                optimizer_ft.step()

            t_loss += loss.item() * imgs.size(0)
            preds = out.argmax(dim=1)
            correct += (preds == lbls).sum().item()
            total += lbls.size(0)

        scheduler_ft.step()
        elapsed = time.time() - start
        val_loss, val_acc, val_f1, _, _ = evaluate_loader(model, val_loader, criterion, device, desc=f"Epoch {epoch}/{args.ft_epochs} [Val]")
        print(f"Epoch {epoch}/{args.ft_epochs} [Fine-Tune] - Train Loss: {t_loss/total:.4f}, Acc: {correct/total*100:.1f}% | Val Acc: {val_acc*100:.1f}%, Macro-F1: {val_f1*100:.1f}% ({elapsed:.1f}s)")

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            save_checkpoint(
                model,
                str(export_path),
                classes=CLASS_NAMES,
                model_name=model_name,
                test_accuracy=float(val_acc),
                val_macro_f1=float(val_f1),
                image_size=args.image_size
            )
            print(f"  --> Saved new best checkpoint with Val Macro-F1: {val_f1*100:.2f}% to {export_path}")

    # Evaluation on Test Dataset
    if test_loader is not None and len(test_samples) > 0:
        print(f"\n--- Final Test Set Clinical Benchmark ({len(test_samples)} Images) ---")
        test_loss, total_acc, macro_f1, y_true, y_pred = evaluate_loader(model, test_loader, criterion, device)
        
        print(f"\n=================================================")
        print(f"  Overall Test Accuracy : {total_acc * 100:.2f}%")
        print(f"  Macro F1-Score        : {macro_f1 * 100:.2f}%")
        print(f"=================================================")

        for i, cname in enumerate(CLASS_NAMES):
            tp = np.sum((y_true == i) & (y_pred == i))
            fp = np.sum((y_true != i) & (y_pred == i))
            fn = np.sum((y_true == i) & (y_pred != i))
            tn = np.sum((y_true != i) & (y_pred != i))

            precision = tp / max(tp + fp, 1)
            recall = tp / max(tp + fn, 1)
            specificity = tn / max(tn + fp, 1)
            f1 = 2 * (precision * recall) / max(precision + recall, 1e-7)

            print(f"\nClass: [{cname}] (Total: {np.sum(y_true == i)})")
            print(f"  Precision    : {precision * 100:.2f}%")
            print(f"  Sensitivity  : {recall * 100:.2f}% (True Positive Rate)")
            print(f"  Specificity  : {specificity * 100:.2f}% (True Negative Rate)")
            print(f"  F1-Score     : {f1 * 100:.2f}%")

        print(f"\nConfusion Matrix (Rows=True, Cols=Predicted):")
        print(f"{'':15s}" + "".join([f"{c:>15s}" for c in CLASS_NAMES]))
        for i, row_name in enumerate(CLASS_NAMES):
            row_str = f"{row_name:15s}"
            for j in range(len(CLASS_NAMES)):
                count = np.sum((y_true == i) & (y_pred == j))
                row_str += f"{count:15d}"
            print(row_str)

    print(f"\n[SUCCESS] SOTA Tuberculosis Model trained and exported to: {export_path}")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train SOTA Tuberculosis Detection Model")
    parser.add_argument("--data-dir", type=str, default="", help="Path to Tuberculosis dataset")
    parser.add_argument("--backbone", type=str, default="convnext_tiny", choices=["convnext_tiny", "densenet121"])
    parser.add_argument("--image-size", type=int, default=384, help="Input resolution (default: 384)")
    parser.add_argument("--batch-size", type=int, default=16, help="Training batch size (default: 16)")
    parser.add_argument("--head-epochs", type=int, default=3, help="Epochs for classifier head warmup")
    parser.add_argument("--ft-epochs", type=int, default=5, help="Epochs for backbone fine-tuning")
    parser.add_argument("--num-workers", type=int, default=0, help="DataLoader workers")
    parser.add_argument("--export-path", type=str, default="", help="Export path for best checkpoint")
    args = parser.parse_args()

    sys.exit(run_training(args))
