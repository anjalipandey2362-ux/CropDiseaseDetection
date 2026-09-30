# Uttar Pradesh Multi-Crop & Plant Disease Detection ML Service

Production-ready machine learning service built with **PyTorch**, **Torchvision (EfficientNet-B0)**, and **FastAPI** for multi-crop identification and crop-conditioned plant disease detection tailored for agriculture in Uttar Pradesh (UP).

---

## 1. Python Version & Hardware Support

- **Python Version**: `3.10` - `3.13`
- **Device Support**: Automatic detection of **CUDA GPU** if available, fallback to **CPU**.

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

---

## 2. Virtual Environment & Installation

### Step 1: Navigate to ML Service folder
```bash
cd ml-service
```

### Step 2: Create virtual environment
```bash
python -m venv venv
```

### Step 3: Activate virtual environment (Windows)
```bash
venv\Scripts\activate
```

*(On macOS/Linux: `source venv/bin/activate`)*

### Step 4: Install dependencies
```bash
pip install -r requirements.txt
```

---

## 3. Dataset Setup & PlantVillage Notice

### Baseline Dataset Setup
To download and extract the initial **PlantVillage** dataset for testing the pipeline:

```bash
python scripts/download_dataset.py
```

> **IMPORTANT NOTICE:**
> PlantVillage is only the baseline test dataset for pipeline verification.
> **PlantVillage does NOT contain all Uttar Pradesh target crops** (e.g., Sugarcane, Mustard, Chickpea, Pigeon Pea, Lentil, Pea).
>
> Custom or verified UP agricultural crop datasets can be placed manually in `dataset/raw/<crop_name>/`. Unknown or unverified datasets will not be mixed automatically into training.

### Prepare Dataset
Group raw images by crop and disease:
```bash
python scripts/prepare_dataset.py
```

### Split Dataset (70% Train, 15% Validation, 15% Test)
Split processed crop images with seed `42` (no duplicate images across splits):
```bash
python scripts/split_dataset.py --input_dir dataset/processed/crop --output_dir dataset/crop
```

---

## 4. Dataset Folder Structure

```text
ml-service/
└── dataset/
    ├── raw/
    ├── processed/
    ├── crop/
    │   ├── train/
    │   ├── val/
    │   └── test/
    └── diseases/
        ├── wheat/
        │   ├── train/
        │   ├── val/
        │   └── test/
        ├── rice/
        │   ├── train/
        │   ├── val/
        │   └── test/
        └── sugarcane/
            ├── train/
            ├── val/
            └── test/
```

---

## 5. Training Models

### PlantVillage 38-Class Baseline Classifier (EfficientNet-B0)
Trains the 38-class PlantVillage crop+disease baseline classifier on `dataset/processed/plantvillage`:
```bash
python training/train_plantvillage.py
```
*(or from project root: `python ml-service/training/train_plantvillage.py`)*

Saves:
- `models/plantvillage_classifier/plantvillage_model.pth`
- `models/plantvillage_classifier/class_names.json`
- `models/plantvillage_classifier/model_metadata.json` (`model_type`: `"plantvillage_38_class_baseline"`, `architecture`: `"EfficientNet-B0"`, `num_classes`: `38`)

> **IMPORTANT STAGING TODO:**
> The `plantvillage_classifier` is a 38-class crop+disease baseline model.
> **TODO**: The final Stage-1 crop classifier must be trained separately using crop-level labels (e.g. wheat, rice, sugarcane, potato, maize, mustard, chickpea, pigeon_pea, lentil, pea).
> Do NOT connect the `plantvillage_classifier` model to the production prediction pipeline as the Stage-1 crop classifier.

### Train Stage 1 Crop Classifier (Crop-Level Labels)
Trains Stage 1 independent crop classifier on crop-level classes in `dataset/crop/`:
```bash
python training/train_crop_classifier.py --data_dir dataset/crop
```

Saves:
- `models/crop_classifier/crop_model.pth`
- `models/crop_classifier/class_names.json`
- `models/crop_classifier/model_metadata.json`

### Train Crop-Specific Disease Model
Trains disease model for a specific crop (e.g., wheat, rice, sugarcane):
```bash
python training/train_disease.py --crop wheat
```
```bash
python training/train_disease.py --crop rice
```

Saves:
- `models/disease_models/<crop>/model.pth`
- `models/disease_models/<crop>/class_names.json`
- `models/disease_models/<crop>/model_metadata.json`
- Updates `models/model_registry.json`

---

## 6. Model Evaluation

Evaluates trained model on the `test` split using `sklearn.metrics`:
```bash
python evaluation/evaluate.py --model_type crop
```

For crop-specific disease model evaluation:
```bash
python evaluation/evaluate.py --model_type disease --crop wheat
```

Outputs generated in `evaluation/results/`:
- `confusion_matrix.png`
- `classification_report.txt`
- `metrics.json`

---

## 7. Standalone Command-Line Inference Test

Test crop identification and disease prediction on any leaf image without running React or Express:

```bash
python tests/test_model.py path/to/sample_leaf.jpg
```

Example Output:
```text
Image: sample_leaf.jpg

Predictions:
  wheat: 0.91
  rice: 0.04
  potato: 0.03
  maize: 0.02

Selected Crop: wheat
Crop Confidence: 0.91
Selected Disease: brown_rust
Disease Confidence: 0.84
Pipeline Status: SUCCESS
```

---

## 8. Starting FastAPI ML Web Service

Start FastAPI server on port 8000:
```bash
uvicorn api.main:app --reload --port 8000
```

API Endpoint: `POST http://localhost:8000/predict` (field `image`)

---

## 9. Model Registry & Expansion

### Adding a New Crop
1. Add raw images to `dataset/raw/<crop_name>/`.
2. Run dataset prepare & split scripts.
3. Train crop classifier (`python training/train_crop.py`).

### Adding a New Disease Model
1. Add disease leaf images to `dataset/diseases/<crop_name>/train/<disease_class>/`.
2. Run `python training/train_disease.py --crop <crop_name>`.
3. The script automatically updates `models/model_registry.json`.

---

## 10. Key Limitations & Design Principles

- **No Fake Confidence**: Softmax probabilities are used directly. If top prediction confidence is below `0.70`, `LOW_CROP_CONFIDENCE` or `LOW_DISEASE_CONFIDENCE` status is returned.
- **Disease Model Availability**: If crop is predicted (e.g. `wheat`) but `models/disease_models/wheat/model.pth` does not exist, the API returns `DISEASE_MODEL_UNAVAILABLE` with `disease: null`. No fallback or fake diseases are generated.
- **Crop-First Architecture**: Disease prediction is strictly conditioned on the crop classifier output.
