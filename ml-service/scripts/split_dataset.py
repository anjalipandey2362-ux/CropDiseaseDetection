import os
import shutil
import random
import argparse
from pathlib import Path

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def split_dataset(input_dir, output_dir, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, seed=42):
    random.seed(seed)
    
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5, "Ratios must sum to 1.0"
    
    if not os.path.exists(input_dir):
        print(f"[-] Input directory does not exist: {input_dir}")
        return

    print(f"[*] Splitting dataset from: {input_dir}")
    print(f"[*] Target split directory: {output_dir}")
    print(f"[*] Ratios - Train: {train_ratio*100:.0f}%, Val: {val_ratio*100:.0f}%, Test: {test_ratio*100:.0f}% (Seed: {seed})")

    # Find class folders
    subfolders = [f for f in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, f))]
    
    if not subfolders:
        print(f"[-] No class subdirectories found in: {input_dir}")
        return

    total_images_all = 0
    total_train_all = 0
    total_val_all = 0
    total_test_all = 0
    class_stats = {}

    for class_name in subfolders:
        class_dir = os.path.join(input_dir, class_name)
        images = [f for f in os.listdir(class_dir) if Path(f).suffix.lower() in VALID_EXTENSIONS]
        
        if not images:
            continue

        # Shuffle deterministically with seed 42
        random.shuffle(images)

        num_images = len(images)
        num_train = int(num_images * train_ratio)
        num_val = int(num_images * val_ratio)
        num_test = num_images - num_train - num_val

        train_imgs = images[:num_train]
        val_imgs = images[num_train:num_train + num_val]
        test_imgs = images[num_train + num_val:]

        # Create split folders
        train_target = os.path.join(output_dir, "train", class_name)
        val_target = os.path.join(output_dir, "val", class_name)
        test_target = os.path.join(output_dir, "test", class_name)

        os.makedirs(train_target, exist_ok=True)
        os.makedirs(val_target, exist_ok=True)
        os.makedirs(test_target, exist_ok=True)

        for img in train_imgs:
            shutil.copy2(os.path.join(class_dir, img), os.path.join(train_target, img))
        for img in val_imgs:
            shutil.copy2(os.path.join(class_dir, img), os.path.join(val_target, img))
        for img in test_imgs:
            shutil.copy2(os.path.join(class_dir, img), os.path.join(test_target, img))

        class_stats[class_name] = {
            "total": num_images,
            "train": len(train_imgs),
            "val": len(val_imgs),
            "test": len(test_imgs)
        }

        total_images_all += num_images
        total_train_all += len(train_imgs)
        total_val_all += len(val_imgs)
        total_test_all += len(test_imgs)

    print("\n===============================================================")
    print(" DATASET SPLIT SUMMARY")
    print("===============================================================")
    print(f"Total images:    {total_images_all}")
    print(f"Training images: {total_train_all}")
    print(f"Validation images: {total_val_all}")
    print(f"Testing images:  {total_test_all}")
    print(f"Number of classes: {len(class_stats)}")
    print("---------------------------------------------------------------")
    print("Images per class:")
    for cls, stats in class_stats.items():
        print(f"  - {cls}: Total={stats['total']} (Train={stats['train']}, Val={stats['val']}, Test={stats['test']})")
    print("===============================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Split dataset into Train (70%), Val (15%), Test (15%).")
    base_dir = os.path.dirname(os.path.dirname(__file__))
    parser.add_argument("--input_dir", type=str, required=True,
                        help="Input directory containing class subfolders (e.g., dataset/processed/crop)")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="Output directory to save train/val/test splits (e.g., dataset/crop)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    split_dataset(args.input_dir, args.output_dir, seed=args.seed)

if __name__ == "__main__":
    main()
