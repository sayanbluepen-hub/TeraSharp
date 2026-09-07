"""Model Evaluation and Inference Module for GeoRes.

Evaluates test accuracy, computes confusion matrix and classification metrics,
and provides sample prediction demonstrations.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

# Ensure project root is present in Python path regardless of working directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch
from sklearn.metrics import classification_report, confusion_matrix

from src.dataset import get_dataloaders
from src.model import build_model, get_device


def evaluate_model(
    checkpoint_path: str = "checkpoints/best_model.pth",
    data_dir: str = "data/eurosat/Dataset",
    batch_size: int = 64,
    subset_fraction: float = 1.0,
) -> Dict:
    """Evaluates trained model against the test dataset."""
    device = get_device()

    if not os.path.isfile(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found at: {checkpoint_path}")

    # Load test split
    _, _, test_loader, classes = get_dataloaders(
        data_dir=data_dir,
        batch_size=batch_size,
        subset_fraction=subset_fraction,
    )
    print(f"Loaded test split with {len(test_loader.dataset)} samples across {len(classes)} classes.")

    # Load model and weights
    model = build_model(num_classes=len(classes), pretrained=False, device=device)
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    all_preds: List[int] = []
    all_targets: List[int] = []

    with torch.no_grad():
        for images, targets in test_loader:
            images = images.to(device)
            outputs = model(images)
            _, preds = outputs.max(1)

            all_preds.extend(preds.cpu().tolist())
            all_targets.extend(targets.tolist())

    # Calculate metrics with explicit labels to handle subsets or unpredicted classes gracefully
    class_indices = list(range(len(classes)))
    report = classification_report(
        all_targets, all_preds, labels=class_indices, target_names=classes, output_dict=True, zero_division=0
    )
    report_text = classification_report(
        all_targets, all_preds, labels=class_indices, target_names=classes, zero_division=0
    )
    cm = confusion_matrix(all_targets, all_preds, labels=class_indices).tolist()

    overall_accuracy = report["accuracy"] * 100.0
    print("\n" + "=" * 60)
    print(f"GEORES EVALUATION REPORT (Overall Accuracy: {overall_accuracy:.2f}%)")
    print("=" * 60)
    print(report_text)

    # Save evaluation summary
    out_dir = os.path.dirname(checkpoint_path) or "checkpoints"
    eval_path = os.path.join(out_dir, "evaluation_report.json")
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump({
            "overall_accuracy": overall_accuracy,
            "classification_report": report,
            "confusion_matrix": cm,
            "classes": classes,
        }, f, indent=2)
    print(f"Evaluation metrics saved to {eval_path}")

    return report


def main():
    parser = argparse.ArgumentParser(description="Evaluate GeoRes EuroSAT Classifier")
    parser.add_argument("--checkpoint", type=str, default="checkpoints/best_model.pth", help="Checkpoint file path")
    parser.add_argument("--data-dir", type=str, default="data/eurosat/Dataset", help="EuroSAT data directory")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--smoke-test", action="store_true", help="Run on smaller test subset")
    args = parser.parse_args()

    fraction = 0.1 if args.smoke_test else 1.0
    evaluate_model(
        checkpoint_path=args.checkpoint,
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        subset_fraction=fraction,
    )


if __name__ == "__main__":
    main()
