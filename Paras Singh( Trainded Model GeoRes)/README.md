# GeoRes: Sentinel-2 Land Use & Land Cover Classification
**Author / Contributor:** Paras Singh  
**Project:** GeoRes (Smart India Hackathon 2026)  
**Model Architecture:** Transfer Learning with ResNet-18 + GeoRes 10-Class Classification Head  
**Test Accuracy:** **98.62%** across 4,050 unseen satellite test images  

---

## Overview

GeoRes provides high-accuracy, automated land use and land cover (LULC) classification from Sentinel-2 satellite imagery. Trained across all 27,000 images of the EuroSAT benchmark on an NVIDIA RTX 3050 GPU, this pipeline achieves state-of-the-art accuracy with sub-20ms inference speed per satellite patch.

### 10 Land Cover Classes Recognized
1. `AnnualCrop` - Seasonal agriculture / rotating crop fields
2. `Forest` - Dense woodland and tree canopies
3. `HerbaceousVegetation` - Wild grasslands and shrublands
4. `Highway` - Motorways and primary transit corridors
5. `Industrial` - Factories, commercial parks, warehouses
6. `Pasture` - Livestock grazing meadows
7. `PermanentCrop` - Orchards and vineyards
8. `Residential` - Housing complexes and suburban infrastructure
9. `River` - Flowing water bodies and river valleys
10. `SeaLake` - Open ocean, lakes, and reservoirs

---

## Model Architecture & Pipeline

- **Feature Extractor**: Deep Residual Network (`ResNet-18`) with ImageNet-pretrained weights.
- **Input Resolution**: 224 x 224 RGB patches with standard ImageNet normalization.
- **Classification Head**: Dropout (`p=0.2`) regularization + 10-dimensional linear projection.
- **Loss Function**: `CrossEntropyLoss` with dynamic inverse-frequency class weighting (mitigates class imbalance penalties).
- **Optimizer & Schedule**: `AdamW` (`lr=1e-4`, `weight_decay=1e-4`) with `CosineAnnealingLR`.
- **Training Progression**: 5 full epochs across 18,900 training and 4,050 validation patches, reaching **98.35% Val Accuracy** and **98.62% Test Accuracy**.

---

## Test Performance Metrics

Evaluated on **4,050 unseen Sentinel-2 satellite patches**:

| Class | Precision | Recall | F1-Score | Test Support |
|---|:---:|:---:|:---:|:---:|
| **AnnualCrop** | 0.99 | 0.99 | 0.99 | 450 |
| **Forest** | 0.99 | 0.99 | 0.99 | 450 |
| **HerbaceousVegetation** | 0.97 | 0.98 | 0.98 | 450 |
| **Highway** | 0.99 | 0.98 | 0.98 | 375 |
| **Industrial** | 0.99 | 1.00 | 1.00 | 375 |
| **Pasture** | 0.98 | 0.98 | 0.98 | 300 |
| **PermanentCrop** | 0.98 | 0.97 | 0.97 | 375 |
| **Residential** | 0.99 | 1.00 | 0.99 | 450 |
| **River** | 0.97 | 0.98 | 0.98 | 375 |
| **SeaLake** | 1.00 | 1.00 | 1.00 | 450 |
| **Overall Accuracy** | — | — | **98.62%** | **4,050** |
| **Macro Average** | **0.99** | **0.99** | **0.99** | **4,050** |

---

## Directory Structure

```
Paras Singh( Trainded Model GeoRes)/
├── ai-docs/                     # Full Documentation-First architecture, decisions, tracking logs
│   ├── Architecture.md
│   ├── Decisions.md
│   ├── Constraints.md
│   ├── Flow.md
│   ├── Handover.md
│   ├── Rollback.md
│   ├── Test-Checklist.md
│   └── tracking/
├── checkpoints/
│   ├── model_weights.pth        # Trained weights checkpoint (98.62% test accuracy)
│   ├── evaluation_report.json   # Full classification report & confusion matrix
│   └── training_history.json    # Loss & accuracy progression across all epochs
├── src/
│   ├── dataset.py               # Dataset discovery, stratified splitting & augmentations
│   ├── model.py                 # ResNet-18 architecture with GeoRes head
│   ├── train.py                 # Training engine with class weighting
│   ├── evaluate.py              # Full evaluation suite
│   └── predict.py               # Single-image top-k inference CLI
├── pyproject.toml               # Package configuration
├── requirements.txt             # Environment dependencies
└── README.md                    # Project overview & usage guide
```

---

## How to Run Inference

### 1. Install Dependencies
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
pip install -r requirements.txt
```

### 2. Predict Any Satellite Image
```bash
python src/predict.py --image path/to/satellite_image.jpg --checkpoint checkpoints/model_weights.pth --top-k 3
```

### 3. Run Test Evaluation
```bash
python src/evaluate.py --checkpoint checkpoints/model_weights.pth
```
