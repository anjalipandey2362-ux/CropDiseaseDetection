import os
import sys
import io
import json
import argparse
import hashlib
from PIL import Image
from pathlib import Path

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def validate_dataset(processed_dir):
    print("===============================================================", flush=True)
    print(" DATASET INTEGRITY & STRATIFIED SPLIT VALIDATION", flush=True)
    print("===============================================================", flush=True)
    print(f"[*] Validating processed dataset at: {processed_dir}\n", flush=True)

    train_dir = os.path.join(processed_dir, "train")
    val_dir = os.path.join(processed_dir, "val")
    test_dir = os.path.join(processed_dir, "test")
    class_json_path = os.path.join(processed_dir, "class_names.json")

    errors = []

    # 1. Check directories and class_names.json exist
    for d_name, d_path in [("train", train_dir), ("val", val_dir), ("test", test_dir)]:
        if not os.path.exists(d_path):
            errors.append(f"Directory missing: '{d_name}' split directory not found at {d_path}")

    if not os.path.exists(class_json_path):
        errors.append(f"Missing class_names.json file at: {class_json_path}")
    else:
        try:
            with open(class_json_path, "r", encoding="utf-8") as f:
                json_classes = json.load(f)
            if len(json_classes) != 38:
                errors.append(f"class_names.json contains {len(json_classes)} classes, expected 38.")
            else:
                print(f"[+] Verified class_names.json exists with 38 class entries.", flush=True)
        except Exception as e:
            errors.append(f"Failed to read class_names.json: {e}")

    if errors:
        for err in errors:
            print(f"[-] ERROR: {err}", flush=True)
        print("\n===============================================================", flush=True)
        print(" DATASET VALIDATION: FAILED", flush=True)
        print("===============================================================\n", flush=True)
        return False

    splits = {
        "train": train_dir,
        "val": val_dir,
        "test": test_dir
    }

    # 2. Check union of classes AND each individual split for all 38 classes
    union_classes = set()
    split_class_counts = {}
    split_counts = {"train": 0, "val": 0, "test": 0}
    corrupt_images = []
    split_hashes = {"train": set(), "val": set(), "test": set()}

    for split_name, split_path in splits.items():
        classes_in_split = sorted([
            c for c in os.listdir(split_path)
            if os.path.isdir(os.path.join(split_path, c)) and not c.startswith(".")
        ])
        count = len(classes_in_split)
        split_class_counts[split_name] = count
        union_classes.update(classes_in_split)

        if count != 38:
            errors.append(f"Split '{split_name}' contains {count} classes, expected EXACTLY 38 classes!")

        print(f"[*] Split '{split_name}': {count} class directories found.", flush=True)

    if len(union_classes) != 38:
        errors.append(f"Union of train/val/test splits contains {len(union_classes)} classes, expected 38!")

    if errors:
        for err in errors:
            print(f"[-] ERROR: {err}", flush=True)
        print("\n===============================================================", flush=True)
        print(" DATASET VALIDATION: FAILED", flush=True)
        print("===============================================================\n", flush=True)
        return False

    # 3. Inspect image files and verify integrity and non-duplication
    print("\n[*] Inspecting and verifying image files across splits...", flush=True)

    canonical_classes = sorted(list(union_classes))
    processed_count = 0

    for split_name, split_path in splits.items():
        for cls in canonical_classes:
            cls_dir = os.path.join(split_path, cls)
            if not os.path.exists(cls_dir):
                errors.append(f"Class '{cls}' missing completely from split '{split_name}'!")
                continue

            img_files = [f for f in os.listdir(cls_dir) if Path(f).suffix.lower() in VALID_EXTENSIONS]
            if len(img_files) == 0:
                errors.append(f"Class '{cls}' in split '{split_name}' has 0 images!")

            for img_file in img_files:
                img_path = os.path.join(cls_dir, img_file)
                split_counts[split_name] += 1
                processed_count += 1

                if processed_count % 10000 == 0:
                    print(f"[*] Verified {processed_count} / 54305 images...", flush=True)

                try:
                    with open(img_path, 'rb') as f:
                        raw_bytes = f.read()

                    # SHA256 duplicate checking
                    f_hash = hashlib.sha256(raw_bytes).hexdigest()
                    split_hashes[split_name].add(f_hash)

                    # Verify PIL image structure from bytes
                    with Image.open(io.BytesIO(raw_bytes)) as img:
                        img.verify()
                except Exception as e:
                    corrupt_images.append((img_path, str(e)))

    # Cross-split duplicate check
    train_val_dups = split_hashes["train"].intersection(split_hashes["val"])
    train_test_dups = split_hashes["train"].intersection(split_hashes["test"])
    val_test_dups = split_hashes["val"].intersection(split_hashes["test"])

    duplicate_cross_split = len(train_val_dups) + len(train_test_dups) + len(val_test_dups)
    total_imgs = sum(split_counts.values())

    print("\n---------------------------------------------------------------", flush=True)
    print(" VALIDATION RESULTS SUMMARY", flush=True)
    print("---------------------------------------------------------------", flush=True)
    print(f"Total verified training images:   {split_counts['train']}", flush=True)
    print(f"Total verified validation images: {split_counts['val']}", flush=True)
    print(f"Total verified testing images:    {split_counts['test']}", flush=True)
    print(f"Total verified images overall:    {total_imgs}", flush=True)
    print(f"Classes in train split:          {split_class_counts['train']} / 38", flush=True)
    print(f"Classes in val split:            {split_class_counts['val']} / 38", flush=True)
    print(f"Classes in test split:           {split_class_counts['test']} / 38", flush=True)
    print("---------------------------------------------------------------", flush=True)

    if corrupt_images:
        print(f"[-] ERROR: Found {len(corrupt_images)} corrupt/unopenable image files:", flush=True)
        for path, err in corrupt_images[:5]:
            print(f"    - {path}: {err}", flush=True)
        errors.append(f"{len(corrupt_images)} corrupt images found.")

    if duplicate_cross_split > 0:
        print(f"[-] ERROR: Found {duplicate_cross_split} duplicate image content items across train/val/test splits!", flush=True)
        errors.append("Duplicate images found across splits.")
    else:
        print("[+] Zero duplicate files found across train/val/test splits!", flush=True)

    if total_imgs != 54305:
        errors.append(f"Total image count is {total_imgs}, expected 54305.")

    print("===============================================================", flush=True)
    if errors:
        for err in errors:
            print(f"[-] ERROR: {err}", flush=True)
        print(" DATASET VALIDATION: FAILED", flush=True)
        print("===============================================================\n", flush=True)
        return False
    else:
        print(" DATASET VALIDATION: PASSED", flush=True)
        print("===============================================================\n", flush=True)
        return True

def main():
    parser = argparse.ArgumentParser(description="Validate dataset integrity and splits.")
    script_dir = Path(__file__).resolve().parent
    ml_service_dir = script_dir.parent
    default_dir = str(ml_service_dir / "dataset" / "processed" / "plantvillage")

    parser.add_argument("--processed_dir", type=str, default=default_dir,
                        help="Path to processed dataset directory to validate")
    args = parser.parse_args()

    success = validate_dataset(args.processed_dir)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
