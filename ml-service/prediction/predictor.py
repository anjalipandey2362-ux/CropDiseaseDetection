import os
import torch
import torchvision.models as models

# Supported UP agricultural crop/disease classes baseline
CLASS_NAMES = [
    {"crop": "Wheat", "disease": "Yellow / Stripe Rust"},
    {"crop": "Wheat", "disease": "Brown / Leaf Rust"},
    {"crop": "Rice / Paddy", "disease": "Rice Blast"},
    {"crop": "Rice / Paddy", "disease": "Bacterial Leaf Blight"},
    {"crop": "Sugarcane", "disease": "Red Rot"},
    {"crop": "Potato", "disease": "Late Blight"},
    {"crop": "Potato", "disease": "Early Blight"},
    {"crop": "Maize", "disease": "Maydis Leaf Blight"},
    {"crop": "Mustard", "disease": "Alternaria Leaf Blight"},
    {"crop": "Chickpea / Gram", "disease": "Fusarium Wilt"},
    {"crop": "Pigeon Pea / Arhar", "disease": "Fusarium Wilt"},
    {"crop": "General Crop", "disease": "Healthy Leaf (No Disease Detected)"}
]

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "crop_classifier", "crop_model.pth")

class CropDiseasePredictor:
    def __init__(self):
        self.model = None
        self.is_loaded = False
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                # Instantiate EfficientNet-B0 architecture
                self.model = models.efficientnet_b0(weights=None)
                
                # Replace classifier head to match number of classes
                in_features = self.model.classifier[1].in_features
                self.model.classifier[1] = torch.nn.Linear(in_features, len(CLASS_NAMES))
                
                # Load trained state dictionary
                self.model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
                self.model.eval()
                self.is_loaded = True
                print(f"✅ EfficientNet-B0 PyTorch Model loaded from {MODEL_PATH}")
            except Exception as e:
                print(f"⚠️ Failed to load model weights from {MODEL_PATH}: {e}")
                self.is_loaded = False
        else:
            print(f"ℹ️ Model file not found at {MODEL_PATH}.")

    def predict(self, image_tensor, filename: str = ""):
        """
        Runs EfficientNet-B0 inference with real softmax probabilities.
        """
        if self.is_loaded and self.model is not None:
            try:
                with torch.no_grad():
                    outputs = self.model(image_tensor)
                    probabilities = torch.softmax(outputs, dim=1)
                    top_prob, top_catid = torch.max(probabilities, 1)
                    
                    idx = top_catid.item()
                    conf = float(top_prob.item())
                    
                    selected_class = CLASS_NAMES[idx if idx < len(CLASS_NAMES) else 0]
                    return {
                        "status": "SUCCESS",
                        "crop": selected_class["crop"],
                        "disease": selected_class["disease"],
                        "confidence": round(conf, 4),
                        "model": "EfficientNet-B0 PyTorch (Trained)"
                    }
            except Exception as e:
                print(f"Error during tensor inference: {e}")
                return {
                    "status": "PREDICTION_ERROR",
                    "crop": None,
                    "disease": None,
                    "confidence": 0.0,
                    "error": str(e)
                }

        return {
            "status": "MODEL_NOT_LOADED",
            "crop": None,
            "disease": None,
            "confidence": 0.0,
            "message": "Model weights not loaded. Training required."
        }

# Global Singleton Predictor
predictor_instance = CropDiseasePredictor()
