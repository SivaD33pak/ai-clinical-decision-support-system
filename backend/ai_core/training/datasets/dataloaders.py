from torch.utils.data import DataLoader
from ai_core.training.datasets.transforms import get_train_transforms, get_val_transforms

def build_dataloaders(train_dataset, val_dataset=None, batch_size: int = 16, num_workers: int = 0):
    """Creates PyTorch DataLoaders for training and validation."""
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=False
    )
    val_loader = None
    if val_dataset is not None:
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=False
        )
    return train_loader, val_loader
