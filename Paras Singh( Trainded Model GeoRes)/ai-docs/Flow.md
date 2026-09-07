# Execution Flow

How execution actually travels across files, functions, and modules.

## Current Flow
1. Pull starter kernel: Downloaded `starter-eurosat-sentinel-2-dataset-0469bae4-9.ipynb`.
2. EuroSAT dataset download:
   - Command: `kaggle datasets download -d raoofnaushad/eurosat-sentinel2-dataset -p data/eurosat/ --unzip`
   - Data lands in `data/eurosat/2750/` with 10 subdirectories for the 10 classes.
3. Classification Pipeline Flow:
   - `src/dataset.py`: Scans `data/eurosat/`, creates stratified train/val/test splits (70/15/15), applies transforms (`Resize(224)`, `RandomHorizontalFlip`, `RandomRotation`, `Normalize`), returns PyTorch `DataLoader`s. Supports stratified subset slicing via `_stratified_subset`.
   - `src/model.py`: Instantiates `ResNet18` backbone, replaces final fully connected layer with `Dropout(0.2) + Linear(in_features, num_classes=10)`. Provides `get_device()` with print-once caching.
   - `src/train.py`: Computes normalized inverse-frequency class weights ($w_c = \frac{N}{C \cdot N_c}$), configures `CrossEntropyLoss(weight=weight_tensor)`, AdamW optimizer, CosineAnnealingLR scheduler. Iterates training batches, evaluates validation loss/accuracy, saves best model checkpoint to `checkpoints/best_model.pth`.
   - `src/evaluate.py`: Loads `checkpoints/best_model.pth` with `weights_only=False`, runs against test split, computes confusion matrix and classification report, saves JSON report to `checkpoints/evaluation_report.json`.
   - `src/predict.py`: Performs top-k inference on single images, outputting confidence scores cleanly.

