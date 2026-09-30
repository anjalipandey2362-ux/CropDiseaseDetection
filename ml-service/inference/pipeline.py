import os
import io
import torch
from PIL import Image, ImageOps
from torchvision import transforms

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training.config import (
    IMAGE_SIZE, DEVICE, IMAGENET_MEAN, IMAGENET_STD, ALL_UP_CROPS,
    CROP_CONFIDENCE_THRESHOLD, DISEASE_CONFIDENCE_THRESHOLD
)
from inference.predict_crop import CropPredictor
from inference.predict_disease import DiseasePredictor

class MLPipeline:
    def __init__(self):
        self.crop_predictor = CropPredictor()
        self.disease_predictor = DiseasePredictor()
        
        self.transform = transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ])

    def preprocess_image_bytes(self, image_bytes):
        """Converts raw image bytes to 224x224 RGB normalized tensor."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image = ImageOps.exif_transpose(image) # Fix camera rotation orientation
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            tensor = self.transform(image)
            return tensor, None
        except Exception as e:
            return None, f"Image processing error: {str(e)}"

    def run_pipeline(self, image_bytes, dev_mode=True):
        # 1. Image Preprocessing & Validation
        tensor, error_msg = self.preprocess_image_bytes(image_bytes)
        if error_msg or tensor is None:
            return {
                "status": "PREPROCESSING_ERROR",
                "crop": None,
                "crop_confidence": 0.0,
                "disease": None,
                "disease_confidence": 0.0,
                "message": error_msg or "Failed to process image file."
            }

        # 2. Stage 1: Crop Classifier
        if not self.crop_predictor.is_loaded:
            return {
                "status": "MODEL_NOT_LOADED",
                "crop": None,
                "crop_confidence": 0.0,
                "disease": None,
                "disease_confidence": 0.0,
                "message": f"Crop classification model is not loaded. {self.crop_predictor.load_error or ''}"
            }

        crop_res = self.crop_predictor.predict(tensor)
        crop_status = crop_res.get("status")
        predicted_crop = crop_res.get("crop")
        crop_conf = crop_res.get("confidence", 0.0)
        crop_top_preds = crop_res.get("top_predictions", [])

        # Debug metadata builder
        debug_info = {
            "device": str(DEVICE),
            "image_size": [IMAGE_SIZE, IMAGE_SIZE],
            "tensor_shape": list(tensor.shape),
            "crop_model_loaded": self.crop_predictor.is_loaded,
            "crop_model_path": self.crop_predictor.model_pth,
            "crop_prediction": predicted_crop,
            "crop_confidence": crop_conf,
            "crop_top_predictions": crop_top_preds,
            "pipeline_stage": "STAGE_1_CROP"
        } if dev_mode else None

        # Check for Low Crop Confidence
        if crop_status == "LOW_CROP_CONFIDENCE" or crop_conf < CROP_CONFIDENCE_THRESHOLD or not predicted_crop:
            return {
                "status": "LOW_CROP_CONFIDENCE",
                "crop": None,
                "crop_confidence": crop_conf,
                "disease": None,
                "disease_confidence": 0.0,
                "message": "Crop could not be identified with high confidence. Please upload a clearer leaf image.",
                "debug": debug_info
            }

        # Check if crop is in unsupported category (not in recognized target agricultural crops)
        normalized_crop = predicted_crop.lower()
        if normalized_crop not in [c.lower() for c in ALL_UP_CROPS]:
            # Check if it's an unrecognized or non-UP crop
            pass

        # 3. Check Disease Model Availability for Predicted Crop
        has_disease_model = self.disease_predictor.is_disease_model_available(predicted_crop)

        if not has_disease_model:
            if dev_mode:
                debug_info["pipeline_stage"] = "STOPPED_DISEASE_MODEL_UNAVAILABLE"
                debug_info["disease_model_status"] = "NOT_TRAINED"

            return {
                "status": "DISEASE_MODEL_UNAVAILABLE",
                "crop": predicted_crop,
                "crop_confidence": crop_conf,
                "disease": None,
                "disease_confidence": 0.0,
                "message": f"Crop identified as '{predicted_crop}', but a trained disease model for this crop is not currently available.",
                "debug": debug_info
            }

        # 4. Stage 2: Crop-Specific Disease Classifier
        disease_res = self.disease_predictor.predict(predicted_crop, tensor)
        disease_status = disease_res.get("status")
        predicted_disease = disease_res.get("disease")
        disease_conf = disease_res.get("confidence", 0.0)
        disease_top_preds = disease_res.get("top_predictions", [])

        if dev_mode:
            debug_info["pipeline_stage"] = "STAGE_2_DISEASE"
            debug_info["disease_prediction"] = predicted_disease
            debug_info["disease_confidence"] = disease_conf
            debug_info["disease_top_predictions"] = disease_top_preds

        # Check for Low Disease Confidence
        if disease_status == "LOW_DISEASE_CONFIDENCE" or disease_conf < DISEASE_CONFIDENCE_THRESHOLD or not predicted_disease:
            return {
                "status": "LOW_DISEASE_CONFIDENCE",
                "crop": predicted_crop,
                "crop_confidence": crop_conf,
                "disease": None,
                "disease_confidence": disease_conf,
                "message": f"Identified crop as '{predicted_crop}', but disease detection confidence was below threshold.",
                "debug": debug_info
            }

        # 5. Success Result
        if dev_mode:
            debug_info["pipeline_stage"] = "SUCCESS"

        return {
            "status": "SUCCESS",
            "crop": predicted_crop,
            "crop_confidence": crop_conf,
            "disease": predicted_disease,
            "disease_confidence": disease_conf,
            "debug": debug_info
        }
