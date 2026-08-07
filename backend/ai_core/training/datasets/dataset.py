# PyTorch Dataset class for Chest X-ray images

class ChestXRayDataset:
    """PyTorch Dataset wrapper for loading Chest X-ray images and labels."""
    def __init__(self, image_paths, labels=None, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)
