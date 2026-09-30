import os
from prediction.model_registry import (
    MODELS_DIR, 
    get_crop_class_names, 
    CROP_DISPLAY_NAMES,
    STATUS_MODEL_NOT_LOADED
)

CROP_MODEL_PATH = os.path.join(MODELS_DIR, "crop_classifier", "crop_model.pth")

class CropPredictor:
    """
    Stage 1: Multi-Crop Independent Crop Classifier.
    Predicts crop species independently from input image tensor.
    Reads class_names.json dynamically.
    """
    def __init__(self):
        self.model = None
        self.is_loaded = False
        self.class_names = []
        self._load_model()

    def _load_model(self):
        self.class_names = get_crop_class_names()
        if os.path.exists(CROP_MODEL_PATH):
            try:
                import torch
                import torchvision.models as models

                weights = models.EfficientNet_B0_Weights.DEFAULT
                self.model = models.efficientnet_b0(weights=None)
                
                in_features = self.model.classifier[1].in_features
                self.model.classifier[1] = torch.nn.Linear(in_features, len(self.class_names))
                
                self.model.load_state_dict(torch.load(CROP_MODEL_PATH, map_location=torch.device('cpu')))
                self.model.eval()
                self.is_loaded = True
                print(f"✅ Stage 1 Crop Classifier loaded successfully from {CROP_MODEL_PATH}")
            except Exception as e:
                print(f"⚠️ Failed to load crop classifier weights: {e}")
                self.is_loaded = False
        else:
            print(f"ℹ️ Stage 1 Crop Classifier weights not found at {CROP_MODEL_PATH}.")

    def predict(self, image_tensor, filename: str = ""):
        """
        Runs PyTorch model inference with real softmax probabilities.
        """
        if self.is_loaded and self.model is not None:
            try:
                import torch
                with torch.no_grad():
                    outputs = self.model(image_tensor)
                    probabilities = torch.softmax(outputs, dim=1)
                    
                    k = min(3, len(self.class_names))
                    topk_probs, topk_indices = torch.topk(probabilities, k=k)
                    
                    top_predictions = []
                    for prob, idx in zip(topk_probs[0], topk_indices[0]):
                        c_id = self.class_names[idx.item()] if idx.item() < len(self.class_names) else "unknown"
                        c_display = CROP_DISPLAY_NAMES.get(c_id, c_id.title())
                        top_predictions.append({
                            "crop_id": c_id,
                            "crop": c_display,
                            "confidence": round(float(prob.item()), 4)
                        })
                    
                    top_crop_id = top_predictions[0]["crop_id"]
                    top_crop_display = top_predictions[0]["crop"]
                    top_conf = top_predictions[0]["confidence"]
                    
                    return {
                        "status": "SUCCESS",
                        "crop_id": top_crop_id,
                        "crop": top_crop_display,
                        "confidence": top_conf,
                        "top_predictions": top_predictions,
                        "model_path": "models/crop_classifier/crop_model.pth"
                    }
            except Exception as e:
                print(f"Error during CropPredictor inference: {e}")
                return {
                    "status": "PREDICTION_ERROR",
                    "crop_id": None,
                    "crop": None,
                    "confidence": 0.0,
                    "top_predictions": [],
                    "error": str(e)
                }

        return {
            "status": STATUS_MODEL_NOT_LOADED,
            "crop_id": None,
            "crop": None,
            "confidence": 0.0,
            "top_predictions": [],
            "message": "Stage-1 Crop Classifier model weights are not loaded. Training required."
        }

crop_predictor_instance = CropPredictor()
