from typing import Tuple, Dict
import torch
import torch.nn as nn
from app.core.logging import logger
from ai_core.training.checkpoint import save_checkpoint

class ModelTrainer:
    """Orchestrates PyTorch model training and validation."""
    def __init__(self, model: nn.Module, train_loader, val_loader=None, criterion=None, optimizer=None, device: str = "cpu"):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.criterion = criterion or nn.CrossEntropyLoss()
        self.optimizer = optimizer or torch.optim.AdamW(filter(lambda p: p.requires_grad, self.model.parameters()), lr=1e-4)
        self.device = device
        self.best_val_loss = float("inf")

    def train_epoch(self) -> Tuple[float, float]:
        self.model.train()
        total_loss, correct, total = 0.0, 0, 0
        for images, labels in self.train_loader:
            images, labels = images.to(self.device), labels.to(self.device)
            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        epoch_loss = total_loss / max(total, 1)
        epoch_acc = correct / max(total, 1)
        return epoch_loss, epoch_acc

    def validate_epoch(self) -> Tuple[float, float]:
        if self.val_loader is None:
            return 0.0, 0.0
        self.model.eval()
        total_loss, correct, total = 0.0, 0, 0
        with torch.no_grad():
            for images, labels in self.val_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)

                total_loss += loss.item() * images.size(0)
                preds = outputs.argmax(dim=1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)

        epoch_loss = total_loss / max(total, 1)
        epoch_acc = correct / max(total, 1)
        return epoch_loss, epoch_acc

    def fit(self, epochs: int = 5, export_path: str = None) -> Dict[str, Any]:
        history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
        for epoch in range(1, epochs + 1):
            t_loss, t_acc = self.train_epoch()
            v_loss, v_acc = self.validate_epoch()
            history["train_loss"].append(t_loss)
            history["train_acc"].append(t_acc)
            history["val_loss"].append(v_loss)
            history["val_acc"].append(v_acc)
            logger.info(f"Epoch {epoch}/{epochs} - Train Loss: {t_loss:.4f}, Train Acc: {t_acc:.4f} | Val Loss: {v_loss:.4f}, Val Acc: {v_acc:.4f}")

            if export_path and (v_loss < self.best_val_loss or self.val_loader is None):
                self.best_val_loss = v_loss
                save_checkpoint(self.model, export_path, epoch=epoch, val_loss=v_loss)
        return history
