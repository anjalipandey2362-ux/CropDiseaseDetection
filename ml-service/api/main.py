import os
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prediction.plantvillage_predictor import pv_predictor_instance

app = FastAPI(
    title="PlantVillage EfficientNet-B0 Crop & Disease Detection ML Service",
    description="Production PyTorch EfficientNet-B0 38-class plant leaf disease classification service.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "service": "PlantVillage EfficientNet-B0 ML Service",
        "status": "online",
        "model_loaded": pv_predictor_instance.is_loaded,
        "device": str(pv_predictor_instance.device),
        "num_classes": len(pv_predictor_instance.class_names)
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy" if pv_predictor_instance.is_loaded else "model_error",
        "device": str(pv_predictor_instance.device),
        "model_loaded": pv_predictor_instance.is_loaded,
        "num_classes": len(pv_predictor_instance.class_names),
        "load_error": pv_predictor_instance.load_error
    }

@app.post("/predict")
async def predict(
    file: UploadFile = File(None),
    image: UploadFile = File(None)
):
    # Support form field name 'file' or 'image'
    upload_item = file or image
    
    # 1. Validate file presence
    if not upload_item or not upload_item.filename:
        return {
            "success": False,
            "error": "No image file uploaded or filename is missing"
        }

    try:
        # Read raw image bytes
        contents = await upload_item.read()
        if len(contents) == 0:
            return {
                "success": False,
                "error": "Uploaded image file is empty"
            }

        # 2. Run inference via pre-loaded EfficientNet-B0 model instance
        result = pv_predictor_instance.predict_bytes(contents)
        return result

    except Exception as e:
        return {
            "success": False,
            "error": f"Unable to process image: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
