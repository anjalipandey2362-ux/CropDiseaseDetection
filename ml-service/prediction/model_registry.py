import os
import json

# Pipeline Status Codes
STATUS_SUCCESS = "SUCCESS"
STATUS_MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
STATUS_IMAGE_ERROR = "IMAGE_ERROR"
STATUS_PREPROCESSING_ERROR = "PREPROCESSING_ERROR"
STATUS_LOW_CROP_CONFIDENCE = "LOW_CROP_CONFIDENCE"
STATUS_UNKNOWN_CROP = "UNKNOWN_CROP"
STATUS_UNSUPPORTED_CROP = "UNSUPPORTED_CROP"
STATUS_DISEASE_MODEL_UNAVAILABLE = "DISEASE_MODEL_UNAVAILABLE"
STATUS_LOW_DISEASE_CONFIDENCE = "LOW_DISEASE_CONFIDENCE"
STATUS_PREDICTION_ERROR = "PREDICTION_ERROR"

# Base Models Directory
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

# Default Fallback Class Lists if training auto-generated JSON files are missing
DEFAULT_CROP_CLASSES = [
    "wheat", "rice", "sugarcane", "potato", "maize",
    "mustard", "chickpea", "pigeon_pea", "lentil", "pea",
    "apple", "tomato", "chili", "brinjal", "mango",
    "non_plant", "unknown"
]

CROP_DISPLAY_NAMES = {
    "wheat": "Wheat",
    "rice": "Rice / Paddy",
    "sugarcane": "Sugarcane",
    "potato": "Potato",
    "maize": "Maize",
    "mustard": "Mustard",
    "chickpea": "Chickpea / Gram",
    "pigeon_pea": "Pigeon Pea / Arhar",
    "lentil": "Lentil",
    "pea": "Pea",
    "apple": "Apple",
    "tomato": "Tomato",
    "chili": "Chili",
    "brinjal": "Brinjal",
    "mango": "Mango",
    "non_plant": "Non-plant",
    "unknown": "Unknown"
}

SUPPORTED_DISEASE_MODELS = ["wheat", "rice", "sugarcane", "potato", "maize", "mustard", "chickpea", "pigeon_pea", "lentil", "pea"]

def get_crop_class_names():
    """
    Dynamically loads crop class names from models/crop_classifier/class_names.json if present.
    """
    json_path = os.path.join(MODELS_DIR, "crop_classifier", "class_names.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load crop class_names.json: {e}")
    return DEFAULT_CROP_CLASSES

def get_disease_class_names(crop_id: str):
    """
    Dynamically loads crop-specific disease class names from models/<crop_id>/class_names.json if present.
    """
    json_path = os.path.join(MODELS_DIR, crop_id, "class_names.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load disease class_names.json for {crop_id}: {e}")
    return None
