"""
Train Stage 1 Independent Crop Classifier (EfficientNet-B0)

TODO:
The final Stage-1 crop classifier must be trained separately using crop-level labels
(e.g., wheat, rice, sugarcane, potato, maize, mustard, chickpea, pigeon_pea, lentil, pea).
The PlantVillage 38-class model (plantvillage_classifier) is a baseline model and must
NOT be used as the production Stage-1 crop classifier.

Usage: python train_crop_classifier.py --data_dir ../dataset/crop --epochs 15
"""

import os
import argparse

SUPPORTED_CROPS = [
    "Wheat", "Rice / Paddy", "Sugarcane", "Potato", "Maize",
    "Mustard", "Chickpea / Gram", "Pigeon Pea / Arhar", "Lentil", "Pea"
]

def train_crop_classifier(data_dir, epochs=25, batch_size=32):
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
        from torch.utils.data import DataLoader, random_split
        import torchvision.transforms as transforms
        import torchvision.models as models
        from dataset import CropDiseaseDataset
    except ImportError:
        print("❌ PyTorch or torchvision not installed.")
        return

    print("=========================================================")
    print("🌾 Training Stage 1 Independent Crop Classifier")
    print(f"📁 Dataset: {data_dir}")
    print("=========================================================")

    if not os.path.exists(data_dir):
        print(f"❌ Dataset path {data_dir} not found.")
        return

    transform = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    dataset = CropDiseaseDataset(root_dir=data_dir, transform=transform)
    if len(dataset) == 0:
        print("❌ No training images found.")
        return

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    weights = models.EfficientNet_B0_Weights.DEFAULT
    model = models.efficientnet_b0(weights=weights)

    # Replace classifier for 10 crop species
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, len(SUPPORTED_CROPS))
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.classifier.parameters(), lr=0.001)

    print(f"🚀 Training Crop Classifier on {device} for {epochs} epochs...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        print(f"Epoch {epoch+1}/{epochs} - Loss: {running_loss/len(train_loader):.4f}")

    save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "crop_classifier", "crop_model.pth")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print(f"💾 Stage 1 Crop Classifier model saved to: {save_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default='../../dataset')
    parser.add_argument('--epochs', type=int, default=25)
    args = parser.parse_args()
    train_crop_classifier(args.data_dir, args.epochs)
