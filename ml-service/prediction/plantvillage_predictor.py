import os
import json
import io
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image, ImageOps

class PlantVillagePredictor:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.class_names = []
        self.is_loaded = False
        self.load_error = None
        
        # Step 3: Exact normalization transforms matching training
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        self._find_and_load_model()

    def _find_and_load_model(self):
        """Locates and loads models/plantvillage_classifier/plantvillage_model.pth"""
        possible_dirs = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "plantvillage_classifier"),
            os.path.join(os.getcwd(), "models", "plantvillage_classifier"),
            os.path.join(os.getcwd(), "ml-service", "models", "plantvillage_classifier"),
            "models/plantvillage_classifier"
        ]
        
        model_dir = None
        for d in possible_dirs:
            pth = os.path.join(d, "plantvillage_model.pth")
            json_path = os.path.join(d, "class_names.json")
            if os.path.exists(pth) and os.path.exists(json_path):
                model_dir = d
                break
                
        if not model_dir:
            self.load_error = "Could not find models/plantvillage_classifier/plantvillage_model.pth"
            print(f"[-] {self.load_error}")
            return
            
        model_pth = os.path.join(model_dir, "plantvillage_model.pth")
        class_json = os.path.join(model_dir, "class_names.json")
        
        try:
            with open(class_json, "r") as f:
                self.class_names = json.load(f)
                
            num_classes = len(self.class_names)
            
            # Step 2: Instantiate EfficientNet-B0 and replace classifier head
            model = models.efficientnet_b0(weights=None)
            in_features = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(in_features, num_classes)
            
            # Load trained weights
            checkpoint = torch.load(model_pth, map_location=self.device)
            if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                model.load_state_dict(checkpoint["model_state_dict"])
            elif isinstance(checkpoint, dict) and "state_dict" in checkpoint:
                model.load_state_dict(checkpoint["state_dict"])
            else:
                model.load_state_dict(checkpoint)
                
            model = model.to(self.device)
            model.eval()
            self.model = model
            self.is_loaded = True
            print(f"[+] Loaded EfficientNet-B0 PlantVillage Model ({num_classes} classes) on {self.device} from {model_pth}")
        except Exception as e:
            self.is_loaded = False
            self.load_error = str(e)
            print(f"[-] Error loading PlantVillage model: {e}")

    def parse_class_name(self, raw_class_name: str):
        """Step 5: Convert PlantVillage class names into user-friendly crop and disease names."""
        if "___" in raw_class_name:
            crop_part, disease_part = raw_class_name.split("___", 1)
        else:
            crop_part, disease_part = raw_class_name, "Unknown"

        # Crop formatting
        crop = crop_part.replace("_", " ").strip()
        if crop.lower() == "corn (maize)":
            crop = "Corn (Maize)"
        elif crop.lower() == "pepper, bell":
            crop = "Pepper (Bell)"
        elif crop.lower() == "cherry (including sour)":
            crop = "Cherry"

        # Disease formatting
        if disease_part.lower() == "healthy":
            disease = "Healthy"
            is_healthy = True
        else:
            is_healthy = False
            disease = disease_part.replace("_", " ").strip()
            disease = " ".join(disease.split())
            words = disease.split(" ")
            cleaned_words = []
            for w in words:
                if w.startswith("(") or w.endswith(")") or "(" in w or ")" in w:
                    cleaned_words.append(w)
                else:
                    cleaned_words.append(w.capitalize())
            disease = " ".join(cleaned_words)
            
        return crop, disease, is_healthy

    def predict_bytes(self, image_bytes: bytes, confidence_threshold: float = 0.60):
        """Runs image prediction using pre-loaded EfficientNet-B0 model."""
        if not self.is_loaded or self.model is None:
            return {
                "success": False,
                "error": f"Model not loaded: {self.load_error or 'Unknown error'}"
            }
            
        try:
            # Step 3: Open image with PIL & convert to RGB
            image = Image.open(io.BytesIO(image_bytes))
            image = ImageOps.exif_transpose(image)
            image = image.convert("RGB")
            
            # Apply preprocessing and add batch dimension
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Step 5: Model inference
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                confidence_tensor, predicted_tensor = torch.max(probabilities, dim=1)
                
            class_index = predicted_tensor.item()
            conf_val = float(confidence_tensor.item())
            conf_pct = round(conf_val * 100, 2)
            raw_class_name = self.class_names[class_index]
            
            crop, disease, is_healthy = self.parse_class_name(raw_class_name)
            
            # Step 6: Confidence handling (60% threshold)
            if conf_val < confidence_threshold:
                return {
                    "success": True,
                    "prediction_status": "low_confidence",
                    "status": "LOW_CONFIDENCE",
                    "crop": crop,
                    "disease": "Uncertain",
                    "confidence": round(conf_val, 4),
                    "confidence_percent": conf_pct,
                    "crop_confidence": round(conf_val, 4),
                    "disease_confidence": round(conf_val, 4),
                    "raw_class_name": raw_class_name,
                    "class_index": class_index,
                    "is_healthy": is_healthy,
                    "message": "The image could not be classified confidently. Please upload a clear image of the affected leaf."
                }

            return {
                "success": True,
                "prediction_status": "success",
                "status": "SUCCESS",
                "crop": crop,
                "disease": disease,
                "confidence": round(conf_val, 4),
                "confidence_percent": conf_pct,
                "crop_confidence": round(conf_val, 4),
                "disease_confidence": round(conf_val, 4),
                "raw_class_name": raw_class_name,
                "class_index": class_index,
                "is_healthy": is_healthy,
                "message": None
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Unable to process image: {str(e)}"
            }

# Singleton instance pre-loaded at module import time
pv_predictor_instance = PlantVillagePredictor()
