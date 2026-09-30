"""
EfficientNet-B0 PyTorch Transfer Learning Training Script
Focus: Uttar Pradesh Agricultural Crop Disease Detection
Usage: python train.py --data_dir ../../dataset --epochs 25 --batch_size 32
"""

import os
import argparse
import time

def train_model(data_dir, epochs=25, batch_size=32, lr=0.001):
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
        from torch.utils.data import DataLoader, random_split
        import torchvision.transforms as transforms
        import torchvision.models as models
        from dataset import CropDiseaseDataset
    except ImportError:
        print("❌ PyTorch or torchvision not installed. Run `pip install -r requirements.txt`.")
        return

    print("=========================================================")
    print("🌾 Starting EfficientNet-B0 Transfer Learning Training")
    print(f"📁 Dataset Path: {data_dir}")
    print(f"⏱️ Epochs: {epochs} | Batch Size: {batch_size} | Learning Rate: {lr}")
    print("=========================================================")

    if not os.path.exists(data_dir):
        print(f"❌ Dataset directory '{data_dir}' not found.")
        print("💡 Please organize real agricultural crop images under dataset/<crop>/<disease>/ directory.")
        return

    # Data augmentation and normalization for training
    data_transforms = {
        'train': transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
    }

    full_dataset = CropDiseaseDataset(root_dir=data_dir, transform=data_transforms['train'])
    num_samples = len(full_dataset)
    num_classes = len(full_dataset.classes)

    if num_samples == 0:
        print("❌ No images found in dataset directory.")
        return

    print(f"📊 Dataset Loaded: {num_samples} images across {num_classes} classes.")

    val_size = int(0.2 * num_samples)
    train_size = num_samples - val_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"🖥️ Using device: {device}")

    # Load pre-trained EfficientNet-B0 weights
    weights = models.EfficientNet_B0_Weights.DEFAULT
    model = models.efficientnet_b0(weights=weights)

    # Freeze base feature extractor layers initially
    for param in model.parameters():
        param.requires_grad = False

    # Replace classifier head for crop disease classes
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.classifier.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    best_acc = 0.0
    best_model_wts = model.state_dict()

    for epoch in range(epochs):
        print(f"\nEpoch {epoch+1}/{epochs}")
        print("-" * 20)

        # Train phase
        model.train()
        running_loss = 0.0
        running_corrects = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()

            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)

        scheduler.step()

        epoch_loss = running_loss / train_size
        epoch_acc = running_corrects.double() / train_size
        print(f"Train Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")

        # Validation phase
        model.eval()
        val_loss = 0.0
        val_corrects = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * inputs.size(0)
                val_corrects += torch.sum(preds == labels.data)

        val_epoch_loss = val_loss / val_size
        val_epoch_acc = val_corrects.double() / val_size
        print(f"Val Loss: {val_epoch_loss:.4f} Acc: {val_epoch_acc:.4f}")

        if val_epoch_acc > best_acc:
            best_acc = val_epoch_acc
            best_model_wts = model.state_dict()

    print(f"\n🏆 Best Validation Accuracy: {best_acc:.4f}")

    # Save model weights to ml-service/model/crop_disease_model.pth
    save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model", "crop_disease_model.pth")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    model.load_state_dict(best_model_wts)
    torch.save(model.state_dict(), save_path)
    print(f"💾 Trained model checkpoint saved to: {save_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train EfficientNet-B0 on Crop Diseases")
    parser.add_argument('--data_dir', type=str, default='../../dataset', help='Path to agricultural dataset')
    parser.add_argument('--epochs', type=int, default=25, help='Number of epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    args = parser.parse_args()

    train_model(args.data_dir, args.epochs, args.batch_size)
