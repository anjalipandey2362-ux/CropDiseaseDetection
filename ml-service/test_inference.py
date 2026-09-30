import os
import sys
import io
import json
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prediction.plantvillage_predictor import pv_predictor_instance

def create_dummy_leaf_image(color=(34, 139, 34), size=(300, 300)):
    """Generates an in-memory synthetic image bytes stream for testing."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def run_tests():
    print("==================================================")
    print("PlantVillage EfficientNet-B0 ML Inference Verification")
    print("==================================================")
    
    # 1. Model Load Check
    print(f"[1] Checking Model Status:")
    print(f"    - Is Loaded: {pv_predictor_instance.is_loaded}")
    print(f"    - Device: {pv_predictor_instance.device}")
    print(f"    - Total Classes: {len(pv_predictor_instance.class_names)}")
    assert pv_predictor_instance.is_loaded, "Model failed to load!"
    
    # 2. Test Synthetic Leaf Image Inference
    print("\n[2] Testing Prediction on Synthetic Image:")
    img_bytes = create_dummy_leaf_image()
    res = pv_predictor_instance.predict_bytes(img_bytes)
    print("    - Response JSON:")
    print(json.dumps(res, indent=6))
    
    assert res.get("success") is True, f"Prediction failed: {res}"
    assert "crop" in res, "Response missing 'crop' field"
    assert "disease" in res, "Response missing 'disease' field"
    assert "confidence" in res, "Response missing 'confidence' field"
    assert "confidence_percent" in res, "Response missing 'confidence_percent' field"
    assert "raw_class_name" in res, "Response missing 'raw_class_name' field"
    assert "class_index" in res, "Response missing 'class_index' field"
    
    # 3. Test Invalid Image Handling
    print("\n[3] Testing Invalid Image Handling:")
    invalid_bytes = b"this is not an image file"
    err_res = pv_predictor_instance.predict_bytes(invalid_bytes)
    print("    - Invalid File Response JSON:")
    print(json.dumps(err_res, indent=6))
    assert err_res.get("success") is False, "Invalid image should return success: False"
    assert "error" in err_res, "Invalid image should return an error message"

    print("\n==================================================")
    print("ALL INFERENCE UNIT TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
