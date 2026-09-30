"""
EfficientNet-B0 Model Evaluation Script
Usage: python evaluate.py --model_path ../model/crop_disease_model.pth --test_dir ../../dataset/test
"""

import os
import argparse

def evaluate_model(model_path, test_dir):
    try:
        import torch
        from torch.utils.data import DataLoader
        import torchvision.transforms as transforms
        import torchvision.models as models
        from sklearn.metrics import classification_report, confusion_matrix
        from dataset import CropDiseaseDataset
    except ImportError:
        print("❌ Scikit-learn, PyTorch or torchvision not installed.")
        return

    print("=========================================================")
    print("📊 Evaluating PlantCare AI Crop Disease Detection Model")
    print(f"📦 Model File: {model_path}")
    print(f"📁 Test Directory: {test_dir}")
    print("=========================================================")

    if not os.path.exists(model_path):
        print(f"❌ Model file {model_path} not found.")
        return

    if not os.path.exists(test_dir):
        print(f"❌ Test dataset directory {test_dir} not found.")
        return

    test_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    test_dataset = CropDiseaseDataset(root_dir=test_dir, transform=test_transform)
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

    num_classes = len(test_dataset.classes)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    model = models.efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = torch.nn.Linear(in_features, num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())

    print("\n📈 Classification Report:")
    print(classification_report(all_labels, all_preds, target_names=test_dataset.classes))

    print("\n🧩 Confusion Matrix:")
    print(confusion_matrix(all_labels, all_preds))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Evaluate Trained Crop Disease Model")
    parser.add_argument('--model_path', type=str, default='../model/crop_disease_model.pth')
    parser.add_argument('--test_dir', type=str, default='../../dataset')
    args = parser.parse_args()

    evaluate_model(args.model_path, args.test_dir)
