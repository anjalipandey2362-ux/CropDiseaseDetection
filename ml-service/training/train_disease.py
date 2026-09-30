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
    DEVICE, IMAGENET_MEAN, IMAGENET_STD, DISEASE_DATASET_DIR,
    DISEASE_MODELS_DIR, MODEL_REGISTRY_PATH
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

def update_model_registry(crop_name, model_path, class_names_path):
    registry = {}
    if os.path.exists(MODEL_REGISTRY_PATH):
        try:
            with open(MODEL_REGISTRY_PATH, "r") as f:
                registry = json.load(f)
        except Exception:
            registry = {}

    rel_model_path = os.path.relpath(model_path, os.path.dirname(MODEL_REGISTRY_PATH)).replace("\\", "/")
    rel_class_path = os.path.relpath(class_names_path, os.path.dirname(MODEL_REGISTRY_PATH)).replace("\\", "/")

    registry[crop_name.lower()] = {
        "model": rel_model_path,
        "classes": rel_class_path,
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(MODEL_REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=4)
    print(f"[+] Updated model registry ({MODEL_REGISTRY_PATH}) for crop '{crop_name}'")

def train_disease_model(crop_name, epochs=EPOCHS, lr=LEARNING_RATE, batch_size=BATCH_SIZE):
    crop_key = crop_name.strip().lower()
    crop_dataset_path = os.path.join(DISEASE_DATASET_DIR, crop_key)
    crop_output_path = os.path.join(DISEASE_MODELS_DIR, crop_key)

    train_dir = os.path.join(crop_dataset_path, "train")
    val_dir = os.path.join(crop_dataset_path, "val")

    if not os.path.exists(train_dir) or not any(os.scandir(train_dir)):
        print(f"[-] Error: Disease training dataset not found for crop '{crop_name}' in '{train_dir}'!")
        print(f"    Please place crop disease images in: dataset/diseases/{crop_key}/train/<disease_name>/")
        print("    Example:")
        print(f"      dataset/diseases/{crop_key}/train/healthy/")
        print(f"      dataset/diseases/{crop_key}/train/rust/")
        return False

    set_seed(RANDOM_SEED)

    train_transform, val_transform = get_transforms()
    train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
    val_dataset = datasets.ImageFolder(val_dir, transform=val_transform) if os.path.exists(val_dir) and any(os.scandir(val_dir)) else None

    class_names = train_dataset.classes
    num_classes = len(class_names)

    print(f"[+] Training Disease Classifier for Crop: '{crop_name.upper()}'")
    print(f"[+] Disease Classes ({num_classes}): {class_names}")
    print(f"[+] Device: {DEVICE}")

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0) if val_dataset else None

    weights = EfficientNet_B0_Weights.DEFAULT
    model = models.efficientnet_b0(weights=weights)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    model = model.to(DEVICE)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    best_val_acc = 0.0
    os.makedirs(crop_output_path, exist_ok=True)

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

        print(f"Epoch {epoch}/{epochs} - Train Loss: {epoch_train_loss:.4f} | Train Acc: {epoch_train_acc:.4f} | Val Loss: {epoch_val_loss:.4f} | Val Acc: {epoch_val_acc:.4f}")

        target_acc = epoch_val_acc if val_loader else epoch_train_acc
        if target_acc >= best_val_acc:
            best_val_acc = target_acc
            model_save_path = os.path.join(crop_output_path, "model.pth")
            torch.save({
                'epoch': epoch,
                'crop': crop_key,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': best_val_acc,
                'class_names': class_names
            }, model_save_path)

    training_time = time.time() - start_time
    print(f"\n[+] Disease Training complete for '{crop_key}' in {training_time / 60:.2f} minutes!")
    print(f"[+] Best Validation Accuracy: {best_val_acc * 100:.2f}%")

    # Save class_names.json
    class_names_path = os.path.join(crop_output_path, "class_names.json")
    with open(class_names_path, "w") as f:
        json.dump(class_names, f, indent=4)

    # Save model_metadata.json
    metadata = {
        "crop": crop_key,
        "model_name": f"{crop_key}_disease_model",
        "architecture": "EfficientNet-B0",
        "image_size": IMAGE_SIZE,
        "disease_classes": class_names,
        "num_classes": num_classes,
        "training_epochs": epochs,
        "learning_rate": lr,
        "batch_size": batch_size,
        "best_val_accuracy": float(best_val_acc),
        "dataset_path": crop_dataset_path,
        "device": str(DEVICE),
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "preprocessing": {
            "resize": [IMAGE_SIZE, IMAGE_SIZE],
            "imagenet_mean": IMAGENET_MEAN,
            "imagenet_std": IMAGENET_STD
        }
    }
    metadata_path = os.path.join(crop_output_path, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)

    # Register in model_registry.json
    model_pth = os.path.join(crop_output_path, "model.pth")
    update_model_registry(crop_key, model_pth, class_names_path)
    return True

def main():
    parser = argparse.ArgumentParser(description="Train Crop-Specific Disease Model.")
    parser.add_argument("--crop", type=str, required=True, help="Crop name (e.g., wheat, rice, sugarcane, potato)")
    parser.add_argument("--epochs", type=int, default=EPOCHS, help="Number of epochs")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE, help="Learning rate")
    parser.add_argument("--batch_size", type=int, default=BATCH_SIZE, help="Batch size")
    args = parser.parse_args()

    train_disease_model(args.crop, args.epochs, args.lr, args.batch_size)

if __name__ == "__main__":
    main()
