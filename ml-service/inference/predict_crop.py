import os
import json
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training.config import (
    IMAGE_SIZE, CROP_CONFIDENCE_THRESHOLD, DEVICE, IMAGENET_MEAN, IMAGENET_STD, CROP_MODEL_DIR
)

class CropPredictor:
    def __init__(self, model_dir=CROP_MODEL_DIR):
        self.model_dir = model_dir
        self.model_pth = os.path.join(model_dir, "crop_model.pth")
        self.class_json = os.path.join(model_dir, "class_names.json")
        self.metadata_json = os.path.join(model_dir, "model_metadata.json")
        
        self.model = None
        self.class_names = []
        self.is_loaded = False
        self.load_error = None
        
        self.transform = transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ])
        
        self._load_model()

    def _verify_model_file(self):
        """Validates model file size, integrity, and class mapping."""
        if not os.path.exists(self.model_pth):
            return False, f"Model file not found at: {self.model_pth}"
        
        if os.path.getsize(self.model_pth) == 0:
            return False, f"Model file is 0 bytes (corrupt) at: {self.model_pth}"
            
        if not os.path.exists(self.class_json):
            return False, f"Class mapping file missing at: {self.class_json}"
            
        return True, "OK"

    def _load_model(self):
        valid, msg = self._verify_model_file()
        if not valid:
            self.is_loaded = False
            self.load_error = msg
            return

        try:
            with open(self.class_json, "r") as f:
                self.class_names = json.load(f)

            num_classes = len(self.class_names)
            
            checkpoint = torch.load(self.model_pth, map_location=DEVICE)
            model = models.efficientnet_b0(weights=None)
            in_features = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(in_features, num_classes)

            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                model.load_state_dict(checkpoint['model_state_dict'])
            else:
                model.load_state_dict(checkpoint)

            model = model.to(DEVICE)
            model.eval()
            self.model = model
            self.is_loaded = True
            self.load_error = None
            print(f"[+] Successfully loaded Crop Classifier model from: {self.model_pth}")
        except Exception as e:
            self.is_loaded = False
            self.load_error = f"Failed to load PyTorch model weights: {str(e)}"
            print(f"[-] Crop Predictor Load Error: {self.load_error}")

    def predict(self, image_tensor):
        if not self.is_loaded or self.model is None:
            return {
                "status": "MODEL_NOT_LOADED",
                "crop": None,
                "confidence": 0.0,
                "top_predictions": [],
                "error": self.load_error or "Crop classifier model not loaded"
            }

        try:
            if image_tensor.dim() == 3:
                image_tensor = image_tensor.unsqueeze(0)

            image_tensor = image_tensor.to(DEVICE)

            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)[0]

            confidences, indices = torch.sort(probabilities, descending=True)

            top_preds = []
            for conf, idx in zip(confidences, indices):
                top_preds.append({
                    "crop": self.class_names[idx.item()],
                    "confidence": round(float(conf.item()), 4)
                })

            top_crop = top_preds[0]["crop"]
            top_conf = top_preds[0]["confidence"]

            if top_conf < CROP_CONFIDENCE_THRESHOLD:
                return {
                    "status": "LOW_CROP_CONFIDENCE",
                    "crop": top_crop,
                    "confidence": top_conf,
                    "top_predictions": top_preds,
                    "message": f"Crop prediction confidence ({top_conf*100:.1f}%) is below threshold ({CROP_CONFIDENCE_THRESHOLD*100:.0f}%)."
                }

            return {
                "status": "SUCCESS",
                "crop": top_crop,
                "confidence": top_conf,
                "top_predictions": top_preds
            }
        except Exception as e:
            return {
                "status": "PREDICTION_ERROR",
                "crop": None,
                "confidence": 0.0,
                "top_predictions": [],
                "error": str(e)
            }
