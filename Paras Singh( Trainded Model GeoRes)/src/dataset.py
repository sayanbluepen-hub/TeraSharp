"""EuroSAT Sentinel-2 Dataset Loader and Transforms.

Handles image discovery, class mapping from filename prefixes,
stratified train/validation/test splitting, and data augmentations.
"""

import os
import random
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ensure project root is present in Python path regardless of execution directory (Audit fix C3)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image
import torch
from torch.utils.data import DataLoader, Dataset
import torchvision.transforms as T

# Standard 10 Land Use / Land Cover classes defined by EuroSAT benchmark
EUROSAT_CLASSES: List[str] = [
    "AnnualCrop",
    "Forest",
    "HerbaceousVegetation",
    "Highway",
    "Industrial",
    "Pasture",
    "PermanentCrop",
    "Residential",
    "River",
    "SeaLake",
]

# ImageNet statistics suited for torchvision pretrained backbones
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_transforms(is_train: bool = True, image_size: int = 224) -> T.Compose:
    """Builds image transformation pipeline.
    
    Training includes random spatial flips and small rotations to mitigate
    overfitting on overhead satellite perspectives (which are rotational invariant).
    """
    if is_train:
        return T.Compose([
            T.Resize((image_size, image_size)),
            T.RandomHorizontalFlip(p=0.5),
            T.RandomVerticalFlip(p=0.5),
            T.RandomRotation(degrees=15),
            T.ToTensor(),
            T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])
    return T.Compose([
        T.Resize((image_size, image_size)),
        T.ToTensor(),
        T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


class EuroSATDataset(Dataset):
    """PyTorch Dataset for EuroSAT Sentinel-2 image patches."""

    def __init__(self, samples: List[Tuple[str, int]], transform: Optional[T.Compose] = None):
        """Args:
            samples: List of (file_path, class_idx) pairs.
            transform: Optional torchvision transform compose pipeline.
        """
        self.samples = samples
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        image_path, label = self.samples[idx]
        # Open image and force 3-channel RGB representation
        with Image.open(image_path) as img:
            image = img.convert("RGB")
        
        if self.transform is not None:
            image = self.transform(image)

        return image, label


def scan_dataset(data_dir: str) -> Tuple[List[Tuple[str, int]], Dict[str, int]]:
    """Discovers all EuroSAT image samples.
    
    Supports both flat files with class prefix (e.g. 'AnnualCrop_123.jpg')
    and subdirectories organized by class name.
    """
    class_to_idx = {cls_name: i for i, cls_name in enumerate(EUROSAT_CLASSES)}
    samples: List[Tuple[str, int]] = []

    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    # Check if images are arranged in subdirectories or flat with prefix
    entries = os.listdir(data_dir)
    has_subdirs = any(os.path.isdir(os.path.join(data_dir, e)) for e in entries)

    if has_subdirs:
        for cls_name, cls_idx in class_to_idx.items():
            cls_folder = os.path.join(data_dir, cls_name)
            if os.path.isdir(cls_folder):
                for fname in os.listdir(cls_folder):
                    if fname.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")):
                        samples.append((os.path.join(cls_folder, fname), cls_idx))
    else:
        for fname in entries:
            if fname.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")):
                cls_name = fname.split("_")[0]
                if cls_name in class_to_idx:
                    samples.append((os.path.join(data_dir, fname), class_to_idx[cls_name]))

    if not samples:
        raise RuntimeError(f"No EuroSAT images discovered in {data_dir}")

    return samples, class_to_idx


def split_samples(
    samples: List[Tuple[str, int]],
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]], List[Tuple[str, int]]]:
    """Splits samples into stratified train, validation, and test sets."""
    rng = random.Random(seed)

    # Group samples by label to guarantee balanced stratification
    by_class: Dict[int, List[Tuple[str, int]]] = {}
    for path, label in samples:
        by_class.setdefault(label, []).append((path, label))

    train_samples, val_samples, test_samples = [], [], []

    for label, class_items in by_class.items():
        rng.shuffle(class_items)
        n_total = len(class_items)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)

        train_samples.extend(class_items[:n_train])
        val_samples.extend(class_items[n_train : n_train + n_val])
        test_samples.extend(class_items[n_train + n_val :])

    return train_samples, val_samples, test_samples


def _stratified_subset(
    samples: List[Tuple[str, int]],
    fraction: float,
    seed: int = 42,
) -> List[Tuple[str, int]]:
    """Takes a proportional subset while preserving class balance.

    Instead of slicing the first N items (which skews toward early classes),
    this groups by label and takes `fraction` samples from each class.
    """
    rng = random.Random(seed)
    by_class: Dict[int, List[Tuple[str, int]]] = {}
    for item in samples:
        by_class.setdefault(item[1], []).append(item)

    subset: List[Tuple[str, int]] = []
    for label in sorted(by_class.keys()):
        items = by_class[label]
        rng.shuffle(items)
        n = max(1, int(len(items) * fraction))
        subset.extend(items[:n])

    return subset


def get_dataloaders(
    data_dir: str = "data/eurosat/Dataset",
    batch_size: int = 64,
    num_workers: int = 0,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    subset_fraction: float = 1.0,
) -> Tuple[DataLoader, DataLoader, DataLoader, List[str]]:
    """Builds and returns DataLoaders for train, val, and test splits."""
    samples, _ = scan_dataset(data_dir)
    train_s, val_s, test_s = split_samples(samples, train_ratio=train_ratio, val_ratio=val_ratio)

    if subset_fraction < 1.0:
        # Stratified subset: sample proportionally from each class to avoid
        # bias toward early classes (audit fix C2)
        train_s = _stratified_subset(train_s, subset_fraction, seed=42)
        val_s = _stratified_subset(val_s, subset_fraction, seed=42)
        test_s = _stratified_subset(test_s, subset_fraction, seed=42)

    train_ds = EuroSATDataset(train_s, transform=get_transforms(is_train=True))
    val_ds = EuroSATDataset(val_s, transform=get_transforms(is_train=False))
    test_ds = EuroSATDataset(test_s, transform=get_transforms(is_train=False))

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    return train_loader, val_loader, test_loader, EUROSAT_CLASSES


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "data/eurosat/Dataset"
    print(f"Testing dataset loader on: {path}")
    train_ld, val_ld, test_ld, classes = get_dataloaders(data_dir=path, batch_size=16)
    print(f"Classes ({len(classes)}): {classes}")
    print(f"Train samples: {len(train_ld.dataset)} | Val: {len(val_ld.dataset)} | Test: {len(test_ld.dataset)}")
    for batch_imgs, batch_lbls in train_ld:
        print(f"Sample Batch - Images shape: {batch_imgs.shape}, Labels shape: {batch_lbls.shape}")
        break
    print("Dataset module self-test PASSED.")
