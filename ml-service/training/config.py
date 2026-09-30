import os
import torch

# Centralized ML Configuration

IMAGE_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 15
LEARNING_RATE = 0.0001
RANDOM_SEED = 42

# Confidence Thresholds
CROP_CONFIDENCE_THRESHOLD = 0.70
DISEASE_CONFIDENCE_THRESHOLD = 0.70

# Hardware Device Selection
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ImageNet Normalization Constants
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Path Definitions
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_DIR = os.path.join(BASE_DIR, "dataset")
CROP_DATASET_DIR = os.path.join(DATASET_DIR, "crop")
DISEASE_DATASET_DIR = os.path.join(DATASET_DIR, "diseases")
PLANTVILLAGE_DATASET_DIR = os.path.join(DATASET_DIR, "processed", "plantvillage")

MODELS_DIR = os.path.join(BASE_DIR, "models")
CROP_MODEL_DIR = os.path.join(MODELS_DIR, "crop_classifier")
PLANTVILLAGE_MODEL_DIR = os.path.join(MODELS_DIR, "plantvillage_classifier")
DISEASE_MODELS_DIR = os.path.join(MODELS_DIR, "disease_models")
MODEL_REGISTRY_PATH = os.path.join(MODELS_DIR, "model_registry.json")

EVALUATION_RESULTS_DIR = os.path.join(BASE_DIR, "evaluation", "results")

# List of target UP Crops for UP agricultural focus
ALL_UP_CROPS = [
    "wheat",
    "rice",
    "sugarcane",
    "potato",
    "maize",
    "mustard",
    "chickpea",
    "pigeon_pea",
    "lentil",
    "pea"
]

