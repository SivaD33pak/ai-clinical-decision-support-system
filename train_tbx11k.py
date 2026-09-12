"""
Clinical-Grade 3-Class ConvNeXt Training Pipeline for TBX11K Benchmark.
Categories:
  0: Normal (Healthy)
  1: Sick & Non-TB (Other Pulmonary Conditions: Pneumonia, Nodules, etc.)
  2: Tuberculosis

Utilizes:
  - ConvNeXt-Tiny @ 384x384 resolution
  - Mixed-precision CUDA acceleration (AMP)
  - Class-weighted CrossEntropyLoss / Focal Loss to balance rare TB cases
  - Cosine Annealing LR Schedule
  - Real-time Clinical Validation: Sensitivity, Specificity, Macro-F1
"""

import os
import sys
import argparse
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import f1_score, recall_score, accuracy_score, confusion_matrix

# Ensure project paths
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from ai_core.models.convnext import ConvNeXtXRay, DEFAULT_TRIAGE_CLASSES
from ai_core.data.tbx11k_dataset import TBX11KDataset

def parse_args():
    parser = argparse.ArgumentParser(description="Train SOTA ConvNeXt on TBX11K")
    parser.add_argument("--data-dir", type=str, default=str(ROOT_DIR / "data" / "raw" / "TBX11K"))
    parser.add_argument("--epochs", type=int, default=8, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size (optimized for RTX 4060 8GB)")
    parser.add_argument("--lr", type=float, default=1e-4, help="Peak learning rate")
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--img-size", type=int, default=384, help="Input resolution")
    parser.add_argument("--num-workers", type=int, default=0, help="DataLoader workers (0 recommended on Windows)")
    parser.add_argument("--save-path", type=str, default=str(ROOT_DIR / "data" / "models" / "best_model.pth"))
    return parser.parse_args()

def calculate_class_weights(dataset):
    labels = [s["label"] for s in dataset.samples]
    counts = np.bincount(labels, minlength=3)
    total = len(labels)
    # Balanced weights: total / (n_classes * count)
    weights = [total / (3.0 * max(1, c)) for c in counts]
    # Normalize
    weights = np.array(weights) / np.sum(weights) * 3.0
    return torch.tensor(weights, dtype=torch.float32), counts

def train_epoch(model, loader, criterion, optimizer, scaler, device):
    model.train()
    running_loss = 0.0
    all_preds, all_targets = [], []

    for batch_idx, (imgs, targets) in enumerate(loader):
        imgs = imgs.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)

        optimizer.zero_grad(set_to_none=True)
        with torch.amp.autocast("cuda", enabled=(device.type == "cuda")):
            outputs = model(imgs)
            loss = criterion(outputs, targets)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        running_loss += loss.item() * imgs.size(0)
        preds = outputs.argmax(dim=1).detach().cpu().numpy()
        all_preds.extend(preds)
        all_targets.extend(targets.detach().cpu().numpy())

    epoch_loss = running_loss / len(loader.dataset)
    acc = accuracy_score(all_targets, all_preds)
    f1 = f1_score(all_targets, all_preds, average="macro", zero_division=0)
    return epoch_loss, acc, f1

@torch.no_grad()
def validate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_preds, all_targets = [], []

    for imgs, targets in loader:
        imgs = imgs.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)

        with torch.amp.autocast("cuda", enabled=(device.type == "cuda")):
            outputs = model(imgs)
            loss = criterion(outputs, targets)

        running_loss += loss.item() * imgs.size(0)
        preds = outputs.argmax(dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_targets.extend(targets.cpu().numpy())

    val_loss = running_loss / len(loader.dataset)
    acc = accuracy_score(all_targets, all_preds)
    macro_f1 = f1_score(all_targets, all_preds, average="macro", zero_division=0)
    
    # Class-wise metrics
    recalls = recall_score(all_targets, all_preds, average=None, zero_division=0)
    tb_recall = float(recalls[2]) if len(recalls) > 2 else 0.0
    
    # TB Specificity (True Negative Rate for TB vs Non-TB)
    tb_true_binary = (np.array(all_targets) == 2).astype(int)
    tb_pred_binary = (np.array(all_preds) == 2).astype(int)
    tn = np.sum((tb_true_binary == 0) & (tb_pred_binary == 0))
    fp = np.sum((tb_true_binary == 0) & (tb_pred_binary == 1))
    tb_specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

    cm = confusion_matrix(all_targets, all_preds, labels=[0, 1, 2])
    return val_loss, acc, macro_f1, tb_recall, tb_specificity, cm

def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print(f"============================================================")
    print(f"      SOTA ConvNeXt-Tiny TBX11K 3-Class Training Pipeline   ")
    print(f"============================================================")
    print(f"Device: {device} ({torch.cuda.get_device_name(0) if device.type == 'cuda' else 'CPU'})")
    print(f"Data directory: {args.data_dir}")
    print(f"Image resolution: {args.img_size}x{args.img_size}")
    print(f"Batch size: {args.batch_size} | Epochs: {args.epochs} | LR: {args.lr}")

    # Datasets
    print("\n[1/4] Loading TBX11K train and validation datasets...")
    train_dataset = TBX11KDataset(args.data_dir, split="train", img_size=args.img_size)
    val_dataset = TBX11KDataset(args.data_dir, split="val", img_size=args.img_size)

    class_weights, counts = calculate_class_weights(train_dataset)
    print(f"  Training samples: {len(train_dataset)} | Normal: {counts[0]}, Sick Non-TB: {counts[1]}, TB: {counts[2]}")
    print(f"  Validation samples: {len(val_dataset)}")
    print(f"  Dynamic Class Weights: {class_weights.tolist()}")

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=(device.type == "cuda"),
        persistent_workers=(args.num_workers > 0)
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=(device.type == "cuda"),
        persistent_workers=(args.num_workers > 0)
    )

    # Model
    print("\n[2/4] Initializing ConvNeXt-Tiny (3-Class Triage)...")
    model = ConvNeXtXRay(num_classes=3, pretrained=True, classes=DEFAULT_TRIAGE_CLASSES).to(device)
    
    # Loss & Optimizer
    criterion = nn.CrossEntropyLoss(weight=class_weights.to(device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)
    scaler = torch.amp.GradScaler("cuda", enabled=(device.type == "cuda"))

    # Training Loop
    print("\n[3/4] Beginning Training Loop...")
    best_macro_f1 = 0.0
    best_tb_sensitivity = 0.0
    os.makedirs(os.path.dirname(args.save_path), exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        start_t = time.time()
        train_loss, train_acc, train_f1 = train_epoch(model, train_loader, criterion, optimizer, scaler, device)
        scheduler.step()

        val_loss, val_acc, val_f1, tb_rec, tb_spec, cm = validate(model, val_loader, criterion, device)
        elapsed = time.time() - start_t

        print(
            f"Epoch [{epoch:02d}/{args.epochs:02d}] ({elapsed:.1f}s) "
            f"Train Loss: {train_loss:.4f} Acc: {train_acc*100:.1f}% F1: {train_f1*100:.1f}% | "
            f"Val Loss: {val_loss:.4f} Acc: {val_acc*100:.1f}% Macro-F1: {val_f1*100:.1f}% | "
            f"TB Sens: {tb_rec*100:.1f}% TB Spec: {tb_spec*100:.1f}%",
            flush=True
        )

        # Save checkpoint if Macro-F1 or TB Recall improves
        if val_f1 > best_macro_f1 or (val_f1 >= best_macro_f1 - 0.02 and tb_rec > best_tb_sensitivity):
            best_macro_f1 = val_f1
            best_tb_sensitivity = tb_rec
            print(f"  [SAVED] New best model -> {args.save_path} (Macro-F1: {val_f1*100:.2f}%, TB Sens: {tb_rec*100:.2f}%)", flush=True)
            torch.save({
                "epoch": epoch,
                "model_name": "ConvNeXt-Tiny",
                "model_state_dict": model.state_dict(),
                "classes": DEFAULT_TRIAGE_CLASSES,
                "val_macro_f1": val_f1,
                "val_accuracy": val_acc,
                "val_tb_sensitivity": tb_rec,
                "val_tb_specificity": tb_spec,
                "confusion_matrix": cm.tolist()
            }, args.save_path)

    print(f"\n[4/4] Training Complete!")
    print(f"Best Validation Macro-F1: {best_macro_f1*100:.2f}% | Best TB Sensitivity: {best_tb_sensitivity*100:.2f}%")
    print(f"Saved weights: {args.save_path}")

if __name__ == "__main__":
    main()
