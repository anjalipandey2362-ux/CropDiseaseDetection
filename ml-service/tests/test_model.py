import os
import sys
import argparse
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference.pipeline import MLPipeline

def main():
    parser = argparse.ArgumentParser(description="Standalone command-line test for Crop & Disease ML pipeline.")
    parser.add_argument("image_path", type=str, help="Path to input crop/leaf image file")
    parser.add_argument("--debug", action="store_true", help="Print verbose AI debug details")
    args = parser.parse_args()

    image_path = args.image_path

    print("\n===============================================================")
    print(" STANDALONE ML MODEL TEST")
    print("===============================================================")
    print(f"Image: {image_path}\n")

    if not os.path.exists(image_path):
        print(f"[-] Error: Image file not found: {image_path}")
        sys.exit(1)

    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        pipeline = MLPipeline()
        result = pipeline.run_pipeline(image_bytes, dev_mode=True)

        status = result.get("status")
        crop = result.get("crop")
        crop_conf = result.get("crop_confidence", 0.0)
        disease = result.get("disease")
        disease_conf = result.get("disease_confidence", 0.0)
        debug = result.get("debug", {})

        top_preds = debug.get("crop_top_predictions", []) if debug else []

        if top_preds:
            print("Predictions:")
            for item in top_preds:
                print(f"  {item['crop']}: {item['confidence']:.2f}")
            print("")

        if crop:
            print(f"Selected Crop: {crop}")
            print(f"Crop Confidence: {crop_conf:.2f}")
        else:
            print("Selected Crop: None (Low Confidence or Model Not Loaded)")

        if disease:
            print(f"Selected Disease: {disease}")
            print(f"Disease Confidence: {disease_conf:.2f}")
        elif status == "DISEASE_MODEL_UNAVAILABLE":
            print("Disease: None (DISEASE_MODEL_UNAVAILABLE)")
        else:
            print(f"Disease: None (Status: {status})")

        print(f"Pipeline Status: {status}")

        if args.debug and debug:
            print("\n---------------------------------------------------------------")
            print(" AI DEBUG INFO:")
            for k, v in debug.items():
                print(f"  {k}: {v}")

        print("===============================================================\n")

    except Exception as e:
        print(f"[-] Error running standalone model test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
