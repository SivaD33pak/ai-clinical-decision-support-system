import os
import sys
import time
from pathlib import Path
from typing import List, Tuple
from PIL import Image
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

# Add backend directory to sys.path
backend_dir = Path(__file__).parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from ai_core.models.densenet import DenseNet121XRay
from ai_core.training.checkpoint import save_checkpoint

CLASS_NAMES = ["Normal", "Pneumonia", "Tuberculosis"]
CLASS_DIR_MAP = {"normal": 0, "pneumonia": 1, "tuberculosis": 2}

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
    for cname in os.listdir(split_dir):
        key = cname.lower()
        if key in CLASS_DIR_MAP:
            label = CLASS_DIR_MAP[key]
            cdir = os.path.join(split_dir, cname)
            for fname in os.listdir(cdir):
                if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                    samples.append((os.path.join(cdir, fname), label))
    return samples

def run_training():
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "raw" / "chest_xray"
    export_path = project_root / "data" / "models" / "best_model.pth"

    print("=" * 60)
    print("AI-CDSS: 3-Class DenseNet121 Training & Fine-Tuning Pipeline")
    print(f"Classes: {CLASS_NAMES}")
    print("=" * 60)

    train_samples = scan_split(str(data_dir / "train"))
    val_samples = scan_split(str(data_dir / "validation"))
    test_samples = scan_split(str(data_dir / "test"))

    print(f"Loaded samples -> Train: {len(train_samples)}, Val: {len(val_samples)}, Test: {len(test_samples)}")

    # Calculate class counts and balanced class weights
    class_counts = [0, 0, 0]
    for _, label in train_samples:
        class_counts[label] += 1
    
    total_train = len(train_samples)
    class_weights = [total_train / (3.0 * max(c, 1)) for c in class_counts]
    weights_tensor = torch.tensor(class_weights, dtype=torch.float32)
    print(f"Train class distribution: Normal={class_counts[0]}, Pneumonia={class_counts[1]}, Tuberculosis={class_counts[2]}")
    print(f"Balanced class weights: {[round(w, 3) for w in class_weights]}")

    # Transforms
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    eval_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_loader = DataLoader(MedicalXRayDataset(train_samples, transform=train_transform), batch_size=32, shuffle=True, num_workers=0)
    val_loader = DataLoader(MedicalXRayDataset(val_samples, transform=eval_transform), batch_size=32, shuffle=False, num_workers=0)
    test_loader = DataLoader(MedicalXRayDataset(test_samples, transform=eval_transform), batch_size=32, shuffle=False, num_workers=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    model = DenseNet121XRay(num_classes=3, pretrained=True, classes=CLASS_NAMES).to(device)
    criterion = nn.CrossEntropyLoss(weight=weights_tensor.to(device))

    # Phase 1: Train classification head with frozen backbone
    print("\n--- Phase 1: Training Classifier Head (Backbone Frozen) ---")
    model.freeze_backbone()
    optimizer = torch.optim.AdamW(model.backbone.classifier.parameters(), lr=1e-3, weight_decay=1e-4)

    for epoch in range(1, 4):
        model.train()
        t_loss, correct, total = 0.0, 0, 0
        start = time.time()
        for batch_idx, (imgs, lbls) in enumerate(train_loader):
            imgs, lbls = imgs.to(device), lbls.to(device)
            optimizer.zero_grad()
            out = model(imgs)
            loss = criterion(out, lbls)
            loss.backward()
            optimizer.step()

            t_loss += loss.item() * imgs.size(0)
            preds = out.argmax(dim=1)
            correct += (preds == lbls).sum().item()
            total += lbls.size(0)

            if (batch_idx + 1) % 50 == 0 or (batch_idx + 1) == len(train_loader):
                print(f"  Batch {batch_idx + 1}/{len(train_loader)} - Loss: {t_loss/total:.4f}, Acc: {correct/total:.4f}")

        elapsed = time.time() - start
        print(f"Epoch {epoch}/3 [Classifier Head] - Train Loss: {t_loss/total:.4f}, Acc: {correct/total:.4f} ({elapsed:.1f}s)")

    # Phase 2: Unfreeze upper dense block for fine-tuning
    print("\n--- Phase 2: Fine-Tuning Top DenseBlock ---")
    for param in model.backbone.features.denseblock4.parameters():
        param.requires_grad = True
    for param in model.backbone.features.norm5.parameters():
        param.requires_grad = True

    optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4, weight_decay=1e-4)

    for epoch in range(1, 3):
        model.train()
        t_loss, correct, total = 0.0, 0, 0
        start = time.time()
        for batch_idx, (imgs, lbls) in enumerate(train_loader):
            imgs, lbls = imgs.to(device), lbls.to(device)
            optimizer.zero_grad()
            out = model(imgs)
            loss = criterion(out, lbls)
            loss.backward()
            optimizer.step()

            t_loss += loss.item() * imgs.size(0)
            preds = out.argmax(dim=1)
            correct += (preds == lbls).sum().item()
            total += lbls.size(0)

            if (batch_idx + 1) % 50 == 0 or (batch_idx + 1) == len(train_loader):
                print(f"  Batch {batch_idx + 1}/{len(train_loader)} - Loss: {t_loss/total:.4f}, Acc: {correct/total:.4f}")

        elapsed = time.time() - start
        print(f"Epoch {epoch}/2 [Fine-Tuning] - Train Loss: {t_loss/total:.4f}, Acc: {correct/total:.4f} ({elapsed:.1f}s)")

    # Evaluation on Test Dataset
    print("\n--- Final Test Set Evaluation (1,044 Images) ---")
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for imgs, lbls in test_loader:
            imgs = imgs.to(device)
            out = model(imgs)
            preds = out.argmax(dim=1).cpu().tolist()
            all_preds.extend(preds)
            all_labels.extend(lbls.tolist())

    # Calculate metrics
    import numpy as np
    y_true = np.array(all_labels)
    y_pred = np.array(all_preds)

    total_acc = (y_true == y_pred).mean()
    print(f"\n==========================================")
    print(f"Overall Test Accuracy: {total_acc * 100:.2f}%")
    print(f"==========================================")

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
        print(f"  Sensitivity  : {recall * 100:.2f}%")
        print(f"  Specificity  : {specificity * 100:.2f}%")
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

    # Export model weights
    save_checkpoint(
        model,
        str(export_path),
        classes=CLASS_NAMES,
        test_accuracy=float(total_acc),
        model_name="DenseNet121-CDSS-v1.0"
    )
    print(f"\n[SUCCESS] Exported best model weights to: {export_path}")

if __name__ == "__main__":
    run_training()
