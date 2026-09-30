"""
PlantVillage 38-Class Baseline Classifier Training Script (EfficientNet-B0)

IMPORTANT ARCHITECTURE & STAGING NOTE:
--------------------------------------
This script trains a 38-class PlantVillage baseline classifier (crop+disease combined labels).
Model outputs are saved to: models/plantvillage_classifier/

TODO: The final Stage-1 crop classifier must be trained separately using crop-level labels
(e.g., wheat, potato, tomato, etc.) rather than combined crop+disease labels.
Do NOT use this 38-class PlantVillage baseline model as the production Stage-1 crop classifier.
"""

import os
import json
import time
import datetime
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torchvision.models import EfficientNet_B0_Weights

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training.config import (
    IMAGE_SIZE, BATCH_SIZE, EPOCHS, LEARNING_RATE, RANDOM_SEED,
    DEVICE, IMAGENET_MEAN, IMAGENET_STD, PLANTVILLAGE_DATASET_DIR, PLANTVILLAGE_MODEL_DIR
)

def set_seed(seed=RANDOM_SEED):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def get_transforms():
    train_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    val_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    return train_transform, val_transform

def build_model(num_classes):
    print(f"[*] Initializing EfficientNet-B0 architecture with ImageNet pretrained weights...")
    weights = EfficientNet_B0_Weights.DEFAULT
    model = models.efficientnet_b0(weights=weights)
    
    # Replace classifier head for 38 PlantVillage crop+disease classes
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    
    return model

def train_plantvillage_classifier(data_dir=PLANTVILLAGE_DATASET_DIR, output_dir=PLANTVILLAGE_MODEL_DIR, epochs=EPOCHS, lr=LEARNING_RATE, batch_size=BATCH_SIZE):
    set_seed(RANDOM_SEED)

    train_dir = os.path.join(data_dir, "train")
    val_dir = os.path.join(data_dir, "val")

    # Search fallback if default relative path needs adjustment
    if not os.path.exists(train_dir) or not any(os.scandir(train_dir)):
        search_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dataset", "processed", "plantvillage"),
            os.path.join(os.getcwd(), "dataset", "processed", "plantvillage"),
            os.path.join(os.getcwd(), "ml-service", "dataset", "processed", "plantvillage")
        ]
        for candidate in search_paths:
            candidate_train = os.path.join(candidate, "train")
            if os.path.exists(candidate_train) and any(os.scandir(candidate_train)):
                data_dir = candidate
                train_dir = candidate_train
                val_dir = os.path.join(candidate, "val")
                print(f"[*] Found processed PlantVillage dataset at: {data_dir}")
                break

    if not os.path.exists(train_dir) or not any(os.scandir(train_dir)):
        print(f"[-] Error: Processed PlantVillage dataset not found in '{train_dir}'!")
        print("    Expected location: dataset/processed/plantvillage")
        return False

    train_transform, val_transform = get_transforms()

    train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
    val_dataset = datasets.ImageFolder(val_dir, transform=val_transform) if os.path.exists(val_dir) and any(os.scandir(val_dir)) else None

    class_names = train_dataset.classes
    num_classes = len(class_names)

    print("=========================================================================")
    print("🌿 Training PlantVillage 38-Class Crop+Disease Baseline Classifier")
    print(f"📁 Dataset Directory : {data_dir}")
    print(f"🏷️  Total Classes     : {num_classes}")
    print(f"🖥️  Target Device     : {DEVICE}")
    print(f"⚙️  Hyperparameters   : Epochs={epochs}, LR={lr}, Batch={batch_size}, Seed={RANDOM_SEED}")
    print("=========================================================================")

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0) if val_dataset else None

    model = build_model(num_classes)
    model = model.to(DEVICE)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    best_val_acc = 0.0
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n[*] Starting Training for {epochs} Epochs...")
    start_time = time.time()

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            correct_train += torch.sum(preds == labels.data).item()
            total_train += labels.size(0)

        epoch_train_loss = running_loss / total_train if total_train > 0 else 0.0
        epoch_train_acc = correct_train / total_train if total_train > 0 else 0.0

        epoch_val_loss = 0.0
        epoch_val_acc = 0.0

        if val_loader:
            model.eval()
            running_val_loss = 0.0
            correct_val = 0
            total_val = 0

            with torch.no_grad():
                for inputs, labels in val_loader:
                    inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)

                    running_val_loss += loss.item() * inputs.size(0)
                    _, preds = torch.max(outputs, 1)
                    correct_val += torch.sum(preds == labels.data).item()
                    total_val += labels.size(0)

            epoch_val_loss = running_val_loss / total_val if total_val > 0 else 0.0
            epoch_val_acc = correct_val / total_val if total_val > 0 else 0.0

        print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {epoch_train_loss:.4f} | Train Acc: {epoch_train_acc:.4f} | Val Loss: {epoch_val_loss:.4f} | Val Acc: {epoch_val_acc:.4f}")

        target_acc = epoch_val_acc if val_loader else epoch_train_acc
        if target_acc >= best_val_acc:
            best_val_acc = target_acc
            model_save_path = os.path.join(output_dir, "plantvillage_model.pth")
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': best_val_acc,
                'class_names': class_names
            }, model_save_path)

    training_time = time.time() - start_time
    print(f"\n[+] Training complete in {training_time / 60:.2f} minutes!")
    print(f"[+] Best Validation Accuracy: {best_val_acc * 100:.2f}%")

    # Save class_names.json
    class_names_path = os.path.join(output_dir, "class_names.json")
    with open(class_names_path, "w") as f:
        json.dump(class_names, f, indent=4)
    print(f"[+] Saved class names mapping to: {class_names_path}")

    # Save model_metadata.json as explicitly required
    metadata = {
        "model_name": "plantvillage_classifier",
        "model_type": "plantvillage_38_class_baseline",
        "architecture": "EfficientNet-B0",
        "num_classes": num_classes,
        "image_size": IMAGE_SIZE,
        "batch_size": batch_size,
        "epochs": epochs,
        "learning_rate": lr,
        "random_seed": RANDOM_SEED,
        "best_val_accuracy": float(best_val_acc),
        "dataset_path": data_dir,
        "device": str(DEVICE),
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "preprocessing": {
            "resize": [IMAGE_SIZE, IMAGE_SIZE],
            "imagenet_mean": IMAGENET_MEAN,
            "imagenet_std": IMAGENET_STD
        }
    }
    metadata_path = os.path.join(output_dir, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"[+] Saved model metadata to: {metadata_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Train PlantVillage 38-Class Baseline Classifier using EfficientNet-B0.")
    parser.add_argument("--data_dir", type=str, default=PLANTVILLAGE_DATASET_DIR, help="Path to processed PlantVillage dataset folder")
    parser.add_argument("--output_dir", type=str, default=PLANTVILLAGE_MODEL_DIR, help="Path to save plantvillage_classifier model files")
    parser.add_argument("--epochs", type=int, default=EPOCHS, help="Number of training epochs")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE, help="Learning rate")
    parser.add_argument("--batch_size", type=int, default=BATCH_SIZE, help="Batch size")
    args = parser.parse_args()

    train_plantvillage_classifier(args.data_dir, args.output_dir, args.epochs, args.lr, args.batch_size)

if __name__ == "__main__":
    main()
