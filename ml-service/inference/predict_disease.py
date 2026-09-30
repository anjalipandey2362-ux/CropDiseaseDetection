import os
import json
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training.config import (
    IMAGE_SIZE, DISEASE_CONFIDENCE_THRESHOLD, DEVICE, IMAGENET_MEAN, IMAGENET_STD,
    DISEASE_MODELS_DIR, MODEL_REGISTRY_PATH
)

class DiseasePredictor:
    def __init__(self, registry_path=MODEL_REGISTRY_PATH):
        self.registry_path = registry_path
        self.loaded_models = {}

    def get_registry(self):
        if not os.path.exists(self.registry_path):
            return {}
        try:
            with open(self.registry_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def is_disease_model_available(self, crop_name):
        if not crop_name:
            return False
        crop_key = crop_name.strip().lower()
        
        # Direct check in filesystem or registry
        crop_model_dir = os.path.join(DISEASE_MODELS_DIR, crop_key)
        model_pth = os.path.join(crop_model_dir, "model.pth")
        class_json = os.path.join(crop_model_dir, "class_names.json")

        if os.path.exists(model_pth) and os.path.getsize(model_pth) > 0 and os.path.exists(class_json):
            return True

        registry = self.get_registry()
        if crop_key in registry:
            entry = registry[crop_key]
            reg_pth = os.path.join(os.path.dirname(self.registry_path), entry["model"])
            if os.path.exists(reg_pth) and os.path.getsize(reg_pth) > 0:
                return True

        return False

    def load_disease_model(self, crop_name):
        crop_key = crop_name.strip().lower()
        if crop_key in self.loaded_models:
            return self.loaded_models[crop_key]

        crop_model_dir = os.path.join(DISEASE_MODELS_DIR, crop_key)
        model_pth = os.path.join(crop_model_dir, "model.pth")
        class_json = os.path.join(crop_model_dir, "class_names.json")

        if not os.path.exists(model_pth) or os.path.getsize(model_pth) == 0 or not os.path.exists(class_json):
            return None

        try:
            with open(class_json, "r") as f:
                class_names = json.load(f)

            num_classes = len(class_names)

            checkpoint = torch.load(model_pth, map_location=DEVICE)
            model = models.efficientnet_b0(weights=None)
            in_features = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(in_features, num_classes)

            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
            else:
                model.load_state_dict(checkpoint)

            model = model.to(DEVICE)
            model.eval()

            model_data = {
                "model": model,
                "class_names": class_names,
                "model_pth": model_pth
            }
            self.loaded_models[crop_key] = model_data
            return model_data
        except Exception as e:
            print(f"[-] Error loading disease model for {crop_name}: {e}")
            return None

    def predict(self, crop_name, image_tensor):
        if not crop_name:
            return {
                "status": "UNSUPPORTED_CROP",
                "disease": None,
                "confidence": 0.0,
                "top_predictions": []
            }

        if not self.is_disease_model_available(crop_name):
            return {
                "status": "DISEASE_MODEL_UNAVAILABLE",
                "disease": None,
                "confidence": 0.0,
                "top_predictions": [],
                "message": f"Disease model for crop '{crop_name}' is not trained or available yet."
            }

        model_data = self.load_disease_model(crop_name)
        if not model_data:
            return {
                "status": "DISEASE_MODEL_UNAVAILABLE",
                "disease": None,
                "confidence": 0.0,
                "top_predictions": [],
                "message": f"Failed to load disease model weights for '{crop_name}'."
            }

        try:
            model = model_data["model"]
            class_names = model_data["class_names"]

            if image_tensor.dim() == 3:
                image_tensor = image_tensor.unsqueeze(0)

            image_tensor = image_tensor.to(DEVICE)

            with torch.no_grad():
                outputs = model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)[0]

            confidences, indices = torch.sort(probabilities, descending=True)

            top_preds = []
            for conf, idx in zip(confidences, indices):
                top_preds.append({
                    "disease": class_names[idx.item()],
                    "confidence": round(float(conf.item()), 4)
                })

            top_disease = top_preds[0]["disease"]
            top_conf = top_preds[0]["confidence"]

            if top_conf < DISEASE_CONFIDENCE_THRESHOLD:
                return {
                    "status": "LOW_DISEASE_CONFIDENCE",
                    "disease": top_disease,
                    "confidence": top_conf,
                    "top_predictions": top_preds,
                    "message": f"Disease prediction confidence ({top_conf*100:.1f}%) is below threshold ({DISEASE_CONFIDENCE_THRESHOLD*100:.0f}%)."
                }

            return {
                "status": "SUCCESS",
                "disease": top_disease,
                "confidence": top_conf,
                "top_predictions": top_preds
            }

        except Exception as e:
            return {
                "status": "PREDICTION_ERROR",
                "disease": None,
                "confidence": 0.0,
                "top_predictions": [],
                "error": str(e)
            }
