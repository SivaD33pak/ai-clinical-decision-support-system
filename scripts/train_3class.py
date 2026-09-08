import os
import sys
import time
from pathlib import Path
from typing import List, Tuple
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

# Add backend directory to sys.path
backend_dir = Path(__file__).parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from ai_core.models.densenet import DenseNet121XRay
from ai_core.training.checkpoint import save_checkpoint

CLASS_NAMES = ["Normal", "Pneumonia", "Tuberculosis"]
CLASS_DIR_MAP = {"normal": 0, "pneumonia": 1, "tuberculosis": 2}

def letterbox_image(image: Image.Image, target_size: int = 224) -> Image.Image:
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
    """Applies auto-contrast to normalize exposure variations across medical scanners."""
    gray = ImageOps.autocontrast(image.convert("L"), cutoff=1)
    return gray.convert("RGB")

class FocalLoss(nn.Module):
    """Focal Loss to counter severe class imbalance and penalize hard examples."""
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

def scan_split(split_dir: str) -> List[Tuple[str, int]]:
    samples = []
    if not os.path.exists(split_dir):
        return samples
    for cname in os.listdir(split_dir):
        key = cname.lower()
        if key in CLASS_DIR_MAP:
            label = CLASS_DIR_MAP[key]
            cdir = os.path.join(split_dir, cname)
            for fname in os.listdir(cdir):
                if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                    samples.append((os.path.join(cdir, fname), label))
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

def run_training():
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "raw" / "chest_xray"
    export_path = project_root / "data" / "models" / "best_model.pth"

    print("=" * 65)
    print("  AI-CDSS: Enhanced Real-World DenseNet121 Training Engine")
    print(f"  Target Classes: {CLASS_NAMES}")
    print("=" * 65)

    train_samples = scan_split(str(data_dir / "train"))
    val_samples = scan_split(str(data_dir / "validation"))
    test_samples = scan_split(str(data_dir / "test"))

    print(f"Dataset Split Sizes -> Train: {len(train_samples)}, Val: {len(val_samples)}, Test: {len(test_samples)}")

    # Calculate class counts and balanced class weights for Focal Loss
    class_counts = [0, 0, 0]
    for _, label in train_samples:
        class_counts[label] += 1
    
    total_train = max(len(train_samples), 1)
    class_weights = [total_train / (3.0 * max(c, 1)) for c in class_counts]
    class_weights = [w / sum(class_weights) * 3.0 for w in class_weights]
    weights_tensor = torch.tensor(class_weights, dtype=torch.float32)
    print(f"Train Class Distribution: Normal={class_counts[0]}, Pneumonia={class_counts[1]}, Tuberculosis={class_counts[2]}")
    print(f"Focal Loss Alpha Weights: {[round(w, 3) for w in class_weights]}")

    # Robust Medical Transforms
    train_transform = transforms.Compose([
        transforms.Lambda(lambda img: enhance_medical_contrast(img)),
        transforms.Lambda(lambda img: letterbox_image(img, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomAffine(degrees=12, translate=(0.05, 0.05), scale=(0.95, 1.05)),
        transforms.ColorJitter(brightness=0.12, contrast=0.12),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        transforms.RandomErasing(p=0.2, scale=(0.02, 0.15), value="random")
    ])

    eval_transform = transforms.Compose([
        transforms.Lambda(lambda img: enhance_medical_contrast(img)),
        transforms.Lambda(lambda img: letterbox_image(img, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_loader = DataLoader(MedicalXRayDataset(train_samples, transform=train_transform), batch_size=32, shuffle=True, num_workers=0)
    val_loader = DataLoader(MedicalXRayDataset(val_samples, transform=eval_transform), batch_size=32, shuffle=False, num_workers=0)
    test_loader = DataLoader(MedicalXRayDataset(test_samples, transform=eval_transform), batch_size=32, shuffle=False, num_workers=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training Compute Device: {device}")

    model = DenseNet121XRay(num_classes=3, pretrained=True, classes=CLASS_NAMES).to(device)
    criterion = FocalLoss(alpha=weights_tensor.to(device), gamma=2.0, label_smoothing=0.05)

    best_val_f1 = -1.0

    # Phase 1: Train classification head with frozen backbone
    print("\n--- Phase 1: Training Classifier Head (Backbone Frozen) ---")
    model.freeze_backbone()
    optimizer_head = torch.optim.AdamW(model.backbone.classifier.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler_head = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer_head, T_max=4)

    for epoch in range(1, 5):
        model.train()
        t_loss, correct, total = 0.0, 0, 0
        start = time.time()
        
        train_iter = tqdm(enumerate(train_loader), total=len(train_loader), desc=f"Epoch {epoch}/4 [Head]", leave=True) if HAS_TQDM else enumerate(train_loader)
        for batch_idx, (imgs, lbls) in train_iter:
            imgs, lbls = imgs.to(device), lbls.to(device)
            optimizer_head.zero_grad()
            out = model(imgs)
            loss = criterion(out, lbls)
            loss.backward()
            optimizer_head.step()

            t_loss += loss.item() * imgs.size(0)
            preds = out.argmax(dim=1)
            correct += (preds == lbls).sum().item()
            total += lbls.size(0)

            if HAS_TQDM:
                train_iter.set_postfix(loss=f"{t_loss/total:.4f}", acc=f"{correct/total*100:.1f}%")
            elif (batch_idx + 1) % 20 == 0 or (batch_idx + 1) == len(train_loader):
                print(f"  [Epoch {epoch}/4 Head] Batch {batch_idx+1}/{len(train_loader)} - Loss: {t_loss/total:.4f}, Acc: {correct/total*100:.1f}%", flush=True)

        scheduler_head.step()
        elapsed = time.time() - start
        val_loss, val_acc, val_f1, _, _ = evaluate_loader(model, val_loader, criterion, device, desc=f"Epoch {epoch}/4 [Val]")
        print(f"Epoch {epoch}/4 [Head] - Train Loss: {t_loss/total:.4f}, Acc: {correct/total*100:.1f}% | Val Acc: {val_acc*100:.1f}%, F1: {val_f1*100:.1f}% ({elapsed:.1f}s)")

    # Phase 2: Unfreeze upper dense blocks for deep fine-tuning
    print("\n--- Phase 2: Fine-Tuning Top DenseBlocks (denseblock3 & denseblock4) ---")
    for param in model.backbone.features.denseblock3.parameters():
        param.requires_grad = True
    for param in model.backbone.features.denseblock4.parameters():
        param.requires_grad = True
    for param in model.backbone.features.norm5.parameters():
        param.requires_grad = True

    optimizer_ft = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4, weight_decay=1e-4)
    scheduler_ft = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer_ft, T_max=4, eta_min=1e-6)

    for epoch in range(1, 5):
        model.train()
        t_loss, correct, total = 0.0, 0, 0
        start = time.time()
        
        train_iter = tqdm(enumerate(train_loader), total=len(train_loader), desc=f"Epoch {epoch}/4 [Fine-Tune]", leave=True) if HAS_TQDM else enumerate(train_loader)
        for batch_idx, (imgs, lbls) in train_iter:
            imgs, lbls = imgs.to(device), lbls.to(device)
            optimizer_ft.zero_grad()
            out = model(imgs)
            loss = criterion(out, lbls)
            loss.backward()
            optimizer_ft.step()

            t_loss += loss.item() * imgs.size(0)
            preds = out.argmax(dim=1)
            correct += (preds == lbls).sum().item()
            total += lbls.size(0)

            if HAS_TQDM:
                train_iter.set_postfix(loss=f"{t_loss/total:.4f}", acc=f"{correct/total*100:.1f}%")
            elif (batch_idx + 1) % 20 == 0 or (batch_idx + 1) == len(train_loader):
                print(f"  [Epoch {epoch}/4 FT] Batch {batch_idx+1}/{len(train_loader)} - Loss: {t_loss/total:.4f}, Acc: {correct/total*100:.1f}%", flush=True)

        scheduler_ft.step()
        elapsed = time.time() - start
        val_loss, val_acc, val_f1, _, _ = evaluate_loader(model, val_loader, criterion, device, desc=f"Epoch {epoch}/4 [Val]")
        print(f"Epoch {epoch}/4 [Fine-Tune] - Train Loss: {t_loss/total:.4f}, Acc: {correct/total*100:.1f}% | Val Acc: {val_acc*100:.1f}%, F1: {val_f1*100:.1f}% ({elapsed:.1f}s)")

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            save_checkpoint(
                model,
                str(export_path),
                classes=CLASS_NAMES,
                test_accuracy=float(val_acc),
                model_name="DenseNet121-CDSS-Enhanced"
            )
            print(f"  --> Saved new best checkpoint with Val Macro-F1: {val_f1*100:.2f}%")

    # Evaluation on Test Dataset
    print("\n--- Final Test Set Clinical Benchmark (1,044 Images) ---")
    test_loss, total_acc, macro_f1, y_true, y_pred = evaluate_loader(model, test_loader, criterion, device)
    
    print(f"\n=================================================")
    print(f"  Overall Test Accuracy : {total_acc * 100:.2f}%")
    print(f"  Macro F1-Score        : {macro_f1 * 100:.2f}%")
    print(f"=================================================")

    # Per-class metrics
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

    # Confusion Matrix
    print(f"\nConfusion Matrix (Rows=True, Cols=Predicted):")
    print(f"{'':15s}" + "".join([f"{c:>15s}" for c in CLASS_NAMES]))
    for i, row_name in enumerate(CLASS_NAMES):
        row_str = f"{row_name:15s}"
        for j in range(3):
            count = np.sum((y_true == i) & (y_pred == j))
            row_str += f"{count:15d}"
        print(row_str)

    print(f"\n[SUCCESS] Enhanced model weights ready at: {export_path}")

if __name__ == "__main__":
    run_training()
