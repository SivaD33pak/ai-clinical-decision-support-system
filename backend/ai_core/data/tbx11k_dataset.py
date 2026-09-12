"""
TBX11K Dataset Loader for PyTorch
Supports 3-class Clinical Triage:
  0: Normal (Healthy)
  1: Sick & Non-TB (Other Pulmonary Diseases: Pneumonia, Nodules, Effusion)
  2: Tuberculosis (Active, Latent, Pulmonary TB)

Compatible with IEEE TPAMI 2023 / CVPR 2020 TBX11K Benchmark.
"""

import os
import json
import glob
from pathlib import Path
from typing import Optional, Callable, Tuple, List, Dict, Any
from PIL import Image
import numpy as np
import torch
from torch.utils.data import Dataset
from torchvision import transforms

CLASS_NAMES = ["Normal", "Sick & Non-TB", "Tuberculosis"]

class TBX11KDataset(Dataset):
    """
    Loads TBX11K dataset images and annotations.
    Parses either COCO-format JSON annotations or text split lists.
    """
    def __init__(
        self,
        root_dir: str,
        split: str = "train",
        transform: Optional[Callable] = None,
        img_size: int = 384,
        return_bbox: bool = False,
        return_meta: bool = False
    ):
        self.root_dir = Path(root_dir)
        self.split = split.lower()
        self.transform = transform
        self.img_size = img_size
        self.return_bbox = return_bbox
        self.return_meta = return_meta
        self.samples: List[Dict[str, Any]] = []

        self._find_and_load_samples()

        if len(self.samples) == 0:
            raise RuntimeError(f"No samples found in {self.root_dir} for split '{self.split}'.")

        # Fallback default transforms if none provided
        if self.transform is None:
            if self.split == "train":
                self.transform = transforms.Compose([
                    transforms.Resize((img_size, img_size)),
                    transforms.RandomHorizontalFlip(p=0.5),
                    transforms.RandomRotation(degrees=7),
                    transforms.ColorJitter(brightness=0.1, contrast=0.15),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
            else:
                self.transform = transforms.Compose([
                    transforms.Resize((img_size, img_size)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])

    def _determine_class(self, filename: str) -> int:
        fname = filename.lower()
        if "health" in fname:
            return 0  # Normal / Healthy
        elif "sick" in fname:
            return 1  # Sick & Non-TB
        elif "tb" in fname:
            return 2  # Tuberculosis
        elif "chncxr" in fname or "mcucxr" in fname:
            # Shenzhen / Montgomery format: ..._1.png is TB, ..._0.png is Normal
            stem = Path(fname).stem
            return 2 if stem.endswith("1") else 0
        return 0

    def _find_and_load_samples(self):
        imgs_dir = self.root_dir / "imgs"
        if not imgs_dir.exists():
            # Check if root_dir itself is imgs or parent
            possible_imgs = list(self.root_dir.rglob("imgs"))
            if possible_imgs:
                imgs_dir = possible_imgs[0]
            else:
                imgs_dir = self.root_dir

        # Strategy 1: Check for text split files (e.g. train.txt, val.txt, test.txt)
        txt_files = list(self.root_dir.rglob(f"*{self.split}*.txt"))
        if txt_files:
            split_file = txt_files[0]
            with open(split_file, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
            for line in lines:
                parts = line.split()
                rel_path = parts[0]
                img_path = imgs_dir / Path(rel_path).name
                if not img_path.exists():
                    img_path = self.root_dir / rel_path
                if img_path.exists():
                    cls_id = self._determine_class(img_path.name)
                    self.samples.append({
                        "path": str(img_path),
                        "label": cls_id,
                        "filename": img_path.name,
                        "bboxes": []
                    })
            if len(self.samples) > 0:
                return

        # Strategy 2: Check for COCO JSON files
        json_pattern = f"*{self.split}*.json"
        json_files = list(self.root_dir.rglob(json_pattern))
        if not json_files and self.split in ["train", "val"]:
            # Check all_trainval.json
            json_files = list(self.root_dir.rglob("*trainval*.json"))

        if json_files:
            ann_file = json_files[0]
            try:
                with open(ann_file, "r", encoding="utf-8") as f:
                    coco_data = json.load(f)
                
                # Index annotations by image_id
                img_bboxes: Dict[int, List[List[float]]] = {}
                for ann in coco_data.get("annotations", []):
                    img_id = ann.get("image_id")
                    bbox = ann.get("bbox", [])
                    if img_id is not None and bbox:
                        img_bboxes.setdefault(img_id, []).append(bbox)

                images = coco_data.get("images", [])
                
                # If using combined trainval file and split requested is train or val, split deterministically
                if "trainval" in ann_file.name.lower() and self.split in ["train", "val"]:
                    # TBX11K: 6,600 train vs 1,800 val (~78.5% / 21.5%)
                    # Seeded deterministic split
                    rng = np.random.RandomState(42)
                    indices = np.arange(len(images))
                    rng.shuffle(indices)
                    num_train = int(len(images) * (6600 / 8400))
                    selected_indices = indices[:num_train] if self.split == "train" else indices[num_train:]
                    images = [images[i] for i in selected_indices]

                for img_info in images:
                    fname = img_info.get("file_name", "")
                    img_id = img_info.get("id")
                    img_path = imgs_dir / fname
                    if not img_path.exists():
                        # Search by filename
                        matches = list(self.root_dir.rglob(fname))
                        if matches:
                            img_path = matches[0]

                    if img_path.exists():
                        cls_id = self._determine_class(fname)
                        bboxes = img_bboxes.get(img_id, [])
                        self.samples.append({
                            "path": str(img_path),
                            "label": cls_id,
                            "filename": fname,
                            "bboxes": bboxes
                        })
                if len(self.samples) > 0:
                    return
            except Exception as e:
                print(f"Warning: Failed parsing {ann_file}: {e}")

        # Strategy 3: Direct filesystem glob fallback
        all_imgs = sorted(list(imgs_dir.glob("*.png")) + list(imgs_dir.glob("*.jpg")))
        if all_imgs:
            rng = np.random.RandomState(42)
            indices = np.arange(len(all_imgs))
            rng.shuffle(indices)
            n_total = len(all_imgs)
            n_train = int(0.70 * n_total)
            n_val = int(0.15 * n_total)
            if self.split == "train":
                chosen = indices[:n_train]
            elif self.split == "val":
                chosen = indices[n_train:n_train+n_val]
            else:
                chosen = indices[n_train+n_val:]
            for idx in chosen:
                p = all_imgs[idx]
                self.samples.append({
                    "path": str(p),
                    "label": self._determine_class(p.name),
                    "filename": p.name,
                    "bboxes": []
                })

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, Dict[str, Any]]:
        sample = self.samples[idx]
        img_path = sample["path"]
        label = sample["label"]

        # Load RGB image
        try:
            image = Image.open(img_path).convert("RGB")
        except Exception:
            # Fallback for corrupt images
            image = Image.new("RGB", (self.img_size, self.img_size), (0, 0, 0))

        if self.transform:
            img_tensor = self.transform(image)
        else:
            img_tensor = transforms.ToTensor()(image)

        if self.return_meta:
            meta = {
                "path": img_path,
                "filename": sample["filename"],
                "label": label,
                "class_name": CLASS_NAMES[label],
                "bboxes": sample.get("bboxes", [])
            }
            return img_tensor, label, meta

        return img_tensor, label
