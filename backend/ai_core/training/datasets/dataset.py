import os
from typing import List, Optional, Tuple
from PIL import Image
import torch
from torch.utils.data import Dataset

class ChestXRayDataset(Dataset):
    """PyTorch Dataset for Chest X-ray classification."""
    def __init__(self, image_paths: List[str], labels: Optional[List[int]] = None, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        label = self.labels[idx] if self.labels is not None else -1
        return image, label

    @classmethod
    def from_directory(cls, root_dir: str, transform=None):
        """Builds dataset by reading class subfolders (e.g. NORMAL/, PNEUMONIA/)."""
        image_paths = []
        labels = []
        class_names = sorted([d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))])
        class_to_idx = {cls_name: i for i, cls_name in enumerate(class_names)}

        for cls_name in class_names:
            cls_dir = os.path.join(root_dir, cls_name)
            for fname in os.listdir(cls_dir):
                if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                    image_paths.append(os.path.join(cls_dir, fname))
                    labels.append(class_to_idx[cls_name])

        dataset = cls(image_paths, labels, transform=transform)
        dataset.classes = class_names
        dataset.class_to_idx = class_to_idx
        return dataset
