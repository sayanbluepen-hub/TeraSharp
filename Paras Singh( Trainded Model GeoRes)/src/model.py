"""GeoRes Classification Model Architecture.

Implements transfer-learning backbone (ResNet-18) tailored for EuroSAT
satellite imagery with custom 10-class prediction head.
"""

from typing import Optional
import torch
import torch.nn as nn
from torchvision.models import ResNet18_Weights, resnet18


# Internal state to ensure device diagnostics are printed only once (Audit fix M1)
_DEVICE_LOGGED = False


def get_device(verbose: bool = False) -> torch.device:
    """Selects CUDA device if available, otherwise falls back to CPU.
    
    Logs device selection on first call or when verbose=True to prevent
    repeated console cluttering in downstream inference/eval scripts.
    """
    global _DEVICE_LOGGED
    if torch.cuda.is_available():
        device = torch.device("cuda")
        if verbose or not _DEVICE_LOGGED:
            gpu_name = torch.cuda.get_device_name(0)
            print(f"[Device] Utilizing CUDA GPU: {gpu_name}")
            _DEVICE_LOGGED = True
    else:
        device = torch.device("cpu")
        if verbose or not _DEVICE_LOGGED:
            print("[Device] CUDA unavailable. Falling back to CPU.")
            _DEVICE_LOGGED = True
    return device


class GeoResClassifier(nn.Module):
    """Deep CNN for Sentinel-2 land use / land cover classification."""

    def __init__(self, num_classes: int = 10, pretrained: bool = True):
        """Args:
            num_classes: Number of target land use categories (10 for EuroSAT).
            pretrained: Whether to load ImageNet pre-trained feature weights.
        """
        super().__init__()
        weights = ResNet18_Weights.DEFAULT if pretrained else None
        self.backbone = resnet18(weights=weights)

        # Replace final classification head with EuroSAT class output
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(p=0.2),  # Regularization to prevent overfitting on satellite features
            nn.Linear(in_features, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass generating unnormalized class logits."""
        return self.backbone(x)


def build_model(num_classes: int = 10, pretrained: bool = True, device: Optional[torch.device] = None) -> GeoResClassifier:
    """Factory function to build and move model to appropriate compute device."""
    dev = device or get_device()
    model = GeoResClassifier(num_classes=num_classes, pretrained=pretrained)
    return model.to(dev)


if __name__ == "__main__":
    print("Testing GeoResClassifier model architecture...")
    dev = get_device()
    model = build_model(num_classes=10, pretrained=False, device=dev)
    dummy_input = torch.randn(4, 3, 64, 64, device=dev)
    output = model(dummy_input)
    print(f"Dummy input shape: {dummy_input.shape}")
    print(f"Output logits shape: {output.shape}")
    assert output.shape == (4, 10), f"Expected shape (4, 10), got {output.shape}"
    print("Model architecture self-test PASSED.")
