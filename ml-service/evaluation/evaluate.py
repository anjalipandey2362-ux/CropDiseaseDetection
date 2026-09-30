import os
import json
import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training.config import (
    IMAGE_SIZE, BATCH_SIZE, DEVICE, IMAGENET_MEAN, IMAGENET_STD,
    CROP_DATASET_DIR, CROP_MODEL_DIR, DISEASE_DATASET_DIR, DISEASE_MODELS_DIR,
    EVALUATION_RESULTS_DIR
)
from evaluation.metrics import calculate_metrics
from evaluation.confusion_matrix import generate_and_save_confusion_matrix

def evaluate_model(model_type="crop", crop_name=None, test_dir=None, model_dir=None, output_dir=EVALUATION_RESULTS_DIR):
    if model_type == "crop":
        test_dir = test_dir or os.path.join(CROP_DATASET_DIR, "test")
        model_dir = model_dir or CROP_MODEL_DIR
        model_pth = os.path.join(model_dir, "crop_model.pth")
        class_json = os.path.join(model_dir, "class_names.json")
    else:
        if not crop_name:
            print("[-] Error: --crop parameter required when evaluating disease model.")
            return False
        crop_key = crop_name.lower()
        test_dir = test_dir or os.path.join(DISEASE_DATASET_DIR, crop_key, "test")
        model_dir = model_dir or os.path.join(DISEASE_MODELS_DIR, crop_key)
        model_pth = os.path.join(model_dir, "model.pth")
        class_json = os.path.join(model_dir, "class_names.json")

    print(f"[*] Starting Evaluation for {model_type.upper()} model...")
    print(f"[*] Test Dataset: {test_dir}")
    print(f"[*] Model File:   {model_pth}")

    if not os.path.exists(model_pth):
        print(f"[-] Error: Saved model file not found: {model_pth}")
        print("    Please train the model first before evaluation.")
        return False

    if not os.path.exists(test_dir) or not any(os.scandir(test_dir)):
        print(f"[-] Error: Test dataset directory empty or missing: {test_dir}")
        print("    Please ensure test data is present.")
        return False

    # Load class names mapping
    with open(class_json, "r") as f:
        class_names = json.load(f)
    num_classes = len(class_names)

    # Transforms
    test_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    test_dataset = datasets.ImageFolder(test_dir, transform=test_transform)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    # Load trained model weights safely
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

    y_true = []
    y_pred = []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(DEVICE)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)

            y_true.extend(labels.cpu().numpy())
            y_pred.extend(preds.cpu().numpy())

    # Calculate metrics
    metrics_dict, report_text = calculate_metrics(y_true, y_pred, target_names=class_names)

    os.makedirs(output_dir, exist_ok=True)

    # Save outputs
    metrics_path = os.path.join(output_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics_dict, f, indent=4)

    report_path = os.path.join(output_dir, "classification_report.txt")
    with open(report_path, "w") as f:
        f.write(f"=== CLASSIFICATION REPORT ({model_type.upper()}) ===\n\n")
        f.write(report_text)

    cm_path = os.path.join(output_dir, "confusion_matrix.png")
    generate_and_save_confusion_matrix(y_true, y_pred, class_names, cm_path)

    print("\n===============================================================")
    print(" EVALUATION RESULTS")
    print("===============================================================")
    print(f" Accuracy:           {metrics_dict['accuracy'] * 100:.2f}%")
    print(f" Weighted Precision: {metrics_dict['precision_weighted']:.4f}")
    print(f" Weighted Recall:    {metrics_dict['recall_weighted']:.4f}")
    print(f" Weighted F1-Score:  {metrics_dict['f1_score_weighted']:.4f}")
    print("---------------------------------------------------------------")
    print(f" Summary saved to: {output_dir}")
    print("===============================================================\n")
    return True

def main():
    parser = argparse.ArgumentParser(description="Evaluate Crop or Disease ML Model on Test Dataset.")
    parser.add_argument("--model_type", type=str, choices=["crop", "disease"], default="crop", help="Type of model to evaluate")
    parser.add_argument("--crop", type=str, default=None, help="Crop name (required if model_type is disease)")
    parser.add_argument("--output_dir", type=str, default=EVALUATION_RESULTS_DIR, help="Directory to save evaluation reports")
    args = parser.parse_args()

    evaluate_model(model_type=args.model_type, crop_name=args.crop, output_dir=args.output_dir)

if __name__ == "__main__":
    main()
