"""Single-image inference utility for GeoRes.

Loads an image and outputs top predicted land cover categories with confidence scores.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

# Ensure project root is present in Python path regardless of working directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image
import torch
import torch.nn.functional as F

from src.dataset import EUROSAT_CLASSES, get_transforms
from src.model import build_model, get_device


def predict_image(
    image_path: str,
    checkpoint_path: str = "checkpoints/best_model.pth",
    top_k: int = 3,
) -> List[Tuple[str, float]]:
    """Predicts top-k classes and confidence percentages for a given image file."""
    device = get_device()

    # Load model architecture and checkpoint
    model = build_model(num_classes=len(EUROSAT_CLASSES), pretrained=False, device=device)
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    # Preprocess image
    transform = get_transforms(is_train=False)
    with Image.open(image_path) as img:
        tensor = transform(img.convert("RGB")).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probabilities = F.softmax(logits, dim=1)[0]
        top_probs, top_indices = torch.topk(probabilities, k=min(top_k, len(EUROSAT_CLASSES)))

    results = []
    for prob, idx in zip(top_probs, top_indices):
        cls_name = EUROSAT_CLASSES[idx.item()]
        conf = prob.item() * 100.0
        results.append((cls_name, conf))

    return results


def main():
    parser = argparse.ArgumentParser(description="Predict Land Cover Class for an Image")
    parser.add_argument("--image", type=str, required=True, help="Path to input satellite image")
    parser.add_argument("--checkpoint", type=str, default="checkpoints/best_model.pth", help="Model checkpoint path")
    parser.add_argument("--top-k", type=int, default=3, help="Number of top predictions to display")
    args = parser.parse_args()

    print(f"\nRunning inference on: {args.image}")
    predictions = predict_image(args.image, checkpoint_path=args.checkpoint, top_k=args.top_k)
    print("\n--- Predictions ---")
    for rank, (cls_name, conf) in enumerate(predictions, start=1):
        print(f"#{rank}: {cls_name:<22} ({conf:.2f}%)")


if __name__ == "__main__":
    main()
