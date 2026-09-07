"""Training Engine for GeoRes Land Cover Classification.

Runs training & validation loops, tracks loss/accuracy, schedules learning rates,
and checkpoints the top-performing model weights.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List

# Ensure project root is present in Python path regardless of working directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

from src.dataset import get_dataloaders
from src.model import build_model, get_device


def train_one_epoch(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> Dict[str, float]:
    """Runs a single training epoch across batches."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    total_batches = len(dataloader)
    for batch_idx, (images, targets) in enumerate(dataloader, start=1):
        images = images.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, preds = outputs.max(1)
        correct += preds.eq(targets).sum().item()
        total += targets.size(0)

        # Log batch progress periodically for training visibility
        if batch_idx % 75 == 0 or batch_idx == total_batches:
            batch_acc = (correct / total) * 100.0
            print(f"  [Batch {batch_idx:03d}/{total_batches:03d}] Loss: {loss.item():.4f} | Running Acc: {batch_acc:.1f}%")

    epoch_loss = running_loss / max(1, total)
    epoch_acc = (correct / max(1, total)) * 100.0
    return {"loss": epoch_loss, "accuracy": epoch_acc}


@torch.no_grad()
def evaluate_epoch(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Dict[str, float]:
    """Evaluates validation loss and accuracy."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, targets in dataloader:
        images = images.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)

        outputs = model(images)
        loss = criterion(outputs, targets)

        running_loss += loss.item() * images.size(0)
        _, preds = outputs.max(1)
        correct += preds.eq(targets).sum().item()
        total += targets.size(0)

    epoch_loss = running_loss / max(1, total)
    epoch_acc = (correct / max(1, total)) * 100.0
    return {"loss": epoch_loss, "accuracy": epoch_acc}


def train_pipeline(
    data_dir: str = "data/eurosat/Dataset",
    epochs: int = 5,
    batch_size: int = 64,
    lr: float = 1e-4,
    weight_decay: float = 1e-4,
    output_dir: str = "checkpoints",
    smoke_test: bool = False,
    pretrained: bool = True,
) -> Dict[str, List[float]]:
    """Executes full training lifecycle."""
    device = get_device()
    os.makedirs(output_dir, exist_ok=True)

    subset_fraction = 0.05 if smoke_test else 1.0
    if smoke_test:
        print("[Smoke-Test] Running on a 5% subset for rapid pipeline verification.")

    train_loader, val_loader, test_loader, classes = get_dataloaders(
        data_dir=data_dir,
        batch_size=batch_size,
        subset_fraction=subset_fraction,
    )
    print(f"Dataset ready. Training samples: {len(train_loader.dataset)}, Validation samples: {len(val_loader.dataset)}")

    model = build_model(num_classes=len(classes), pretrained=pretrained, device=device)

    # Compute inverse-frequency class weights to balance loss penalties (Audit fix S1).
    # Assumes train_loader.dataset exposes .samples as (path, class_idx) pairs.
    # Weight formula: w_c = N / (C * N_c), so minority classes receive higher gradients.
    class_counts = [0] * len(classes)
    for _, lbl in train_loader.dataset.samples:
        class_counts[lbl] += 1
    total_samples = len(train_loader.dataset.samples)
    num_classes = len(classes)
    class_weights = [
        total_samples / (num_classes * max(1, count))
        for count in class_counts
    ]
    weight_tensor = torch.tensor(class_weights, dtype=torch.float32, device=device)
    criterion = nn.CrossEntropyLoss(weight=weight_tensor)

    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs)

    best_val_acc = 0.0
    history: Dict[str, List[float]] = {
        "train_loss": [], "train_acc": [],
        "val_loss": [], "val_acc": []
    }

    start_time = time.time()
    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        train_metrics = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_metrics = evaluate_epoch(model, val_loader, criterion, device)
        scheduler.step()

        history["train_loss"].append(train_metrics["loss"])
        history["train_acc"].append(train_metrics["accuracy"])
        history["val_loss"].append(val_metrics["loss"])
        history["val_acc"].append(val_metrics["accuracy"])

        elapsed = time.time() - epoch_start
        print(
            f"Epoch [{epoch:02d}/{epochs:02d}] ({elapsed:.1f}s) | "
            f"Train Loss: {train_metrics['loss']:.4f}, Train Acc: {train_metrics['accuracy']:.2f}% | "
            f"Val Loss: {val_metrics['loss']:.4f}, Val Acc: {val_metrics['accuracy']:.2f}%"
        )

        # Save best model checkpoint
        if val_metrics["accuracy"] > best_val_acc:
            best_val_acc = val_metrics["accuracy"]
            checkpoint_path = os.path.join(output_dir, "best_model.pth")
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_accuracy": best_val_acc,
                "classes": classes,
            }, checkpoint_path)
            print(f" -> Best checkpoint saved with Val Acc: {best_val_acc:.2f}% at {checkpoint_path}")

    total_time = time.time() - start_time
    print(f"\nTraining completed in {total_time/60:.2f} minutes. Best Val Acc: {best_val_acc:.2f}%.")

    # Persist metrics history
    history_path = os.path.join(output_dir, "training_history.json")
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    return history


def main():
    parser = argparse.ArgumentParser(description="Train GeoRes EuroSAT Classifier")
    parser.add_argument("--data-dir", type=str, default="data/eurosat/Dataset", help="Path to EuroSAT dataset")
    parser.add_argument("--epochs", type=int, default=5, help="Number of epochs to train")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--output-dir", type=str, default="checkpoints", help="Output checkpoint directory")
    parser.add_argument("--smoke-test", action="store_true", help="Run fast test on a small subset")
    parser.add_argument("--no-pretrained", action="store_true", help="Disable ImageNet pre-training")
    args = parser.parse_args()

    train_pipeline(
        data_dir=args.data_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        output_dir=args.output_dir,
        smoke_test=args.smoke_test,
        pretrained=not args.no_pretrained,
    )


if __name__ == "__main__":
    main()
