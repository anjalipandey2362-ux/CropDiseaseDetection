"""
Train Stage 2 Crop-Conditioned Disease Classifier (EfficientNet-B0)
Usage: python train_disease_classifier.py --crop wheat --data_dir ../../dataset/wheat --epochs 25
"""

import os
import argparse

def train_disease_classifier(crop_name, data_dir, epochs=25, batch_size=32):
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

    crop_id = crop_name.lower().split(" ")[0].replace("/", "").strip()
    print("=========================================================")
    print(f"🦠 Training Stage 2 Disease Classifier for Crop: {crop_name} ({crop_id})")
    print(f"📁 Dataset Path: {data_dir}")
    print("=========================================================")

    if not os.path.exists(data_dir):
        print(f"❌ Crop dataset directory {data_dir} not found.")
        return

    transform = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    dataset = CropDiseaseDataset(root_dir=data_dir, transform=transform)
    num_classes = len(dataset.classes)
    if num_classes == 0:
        print("❌ No disease folders found for crop.")
        return

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    weights = models.EfficientNet_B0_Weights.DEFAULT
    model = models.efficientnet_b0(weights=weights)

    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.classifier.parameters(), lr=0.001)

    print(f"🚀 Training {crop_name} Disease Model for {epochs} epochs...")
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

    save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", crop_id)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "disease_model.pth")
    torch.save(model.state_dict(), save_path)
    print(f"💾 Stage 2 Disease Model for {crop_name} saved to: {save_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--crop', type=str, required=True, help='Target crop (e.g. wheat, sugarcane, potato, rice, maize)')
    parser.add_argument('--data_dir', type=str, required=True, help='Path to crop disease folders')
    parser.add_argument('--epochs', type=int, default=25)
    args = parser.parse_args()
    train_disease_classifier(args.crop, args.data_dir, args.epochs)
