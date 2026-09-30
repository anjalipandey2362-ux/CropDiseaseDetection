import os
from prediction.model_registry import MODELS_DIR, get_disease_class_names

class DiseasePredictor:
    """
    Stage 2: Crop-Conditioned Disease Classifier.
    Runs inference ONLY on the PyTorch model registered for the predicted crop using real softmax probabilities.
    """
    def predict(self, crop_id: str, image_tensor, filename: str = ""):
        """
        Runs crop-conditioned disease classification using real PyTorch model probabilities.
        """
        if not crop_id:
            return {
                "status": "INVALID_CROP",
                "disease": None,
                "confidence": 0.0,
                "top_predictions": []
            }

        clean_crop_id = crop_id.lower().replace("/", "").replace("-", "_").split(" ")[0].strip()
        model_path = os.path.join(MODELS_DIR, clean_crop_id, "disease_model.pth")
        disease_classes = get_disease_class_names(clean_crop_id)

        if not disease_classes or not os.path.exists(model_path):
            return {
                "status": "DISEASE_MODEL_UNAVAILABLE",
                "disease": None,
                "confidence": 0.0,
                "top_predictions": [],
                "message": f"Trained disease classifier model for '{clean_crop_id}' is not available."
            }

        try:
            import torch
            import torchvision.models as models

            weights = models.EfficientNet_B0_Weights.DEFAULT
            model = models.efficientnet_b0(weights=None)

            in_features = model.classifier[1].in_features
            model.classifier[1] = torch.nn.Linear(in_features, len(disease_classes))

            model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            model.eval()

            with torch.no_grad():
                outputs = model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                
                k = min(3, len(disease_classes))
                topk_probs, topk_indices = torch.topk(probabilities, k=k)

                top_preds = []
                for prob, idx in zip(topk_probs[0], topk_indices[0]):
                    d_name = disease_classes[idx.item()] if idx.item() < len(disease_classes) else "unknown"
                    top_preds.append({
                        "disease": d_name,
                        "confidence": round(float(prob.item()), 4)
                    })

                top_disease = top_preds[0]["disease"]
                top_conf = top_preds[0]["confidence"]

                return {
                    "status": "SUCCESS",
                    "disease": top_disease,
                    "confidence": top_conf,
                    "top_predictions": top_preds,
                    "model_path": f"models/{clean_crop_id}/disease_model.pth"
                }
        except Exception as e:
            print(f"Error in DiseasePredictor for {clean_crop_id}: {e}")
            return {
                "status": "PREDICTION_ERROR",
                "disease": None,
                "confidence": 0.0,
                "top_predictions": [],
                "error": str(e)
            }

disease_predictor_instance = DiseasePredictor()
