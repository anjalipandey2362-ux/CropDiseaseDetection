import os
import shutil
import random
import json
import argparse
import time
import stat
import hashlib
from pathlib import Path

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
RANDOM_SEED = 42

def remove_readonly(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def clean_processed_directory(processed_dir):
    """Safely removes and clears ONLY dataset/processed/plantvillage contents."""
    if os.path.exists(processed_dir):
        for item in os.listdir(processed_dir):
            item_path = os.path.join(processed_dir, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, onexc=remove_readonly)
                else:
                    os.chmod(item_path, stat.S_IWRITE)
                    os.remove(item_path)
            except Exception as e:
                print(f"[!] Warning cleaning {item_path}: {e}")

def safe_copy(src, dst):
    """Ensures parent directory exists and copies file cleanly."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    for attempt in range(5):
        try:
            shutil.copy2(src, dst)
            return
        except PermissionError:
            time.sleep(0.02)
        except Exception:
            try:
                shutil.copyfile(src, dst)
                return
            except Exception:
                time.sleep(0.02)

def find_raw_color_dir(start_dir=None):
    """Searches for raw PlantVillage color directory."""
    script_dir = Path(__file__).resolve().parent
    ml_service_dir = script_dir.parent
    workspace_dir = ml_service_dir.parent

    search_roots = []
    if start_dir:
        search_roots.append(Path(start_dir))
    search_roots.extend([
        ml_service_dir / "dataset" / "raw",
        workspace_dir / "dataset" / "raw",
        ml_service_dir / "dataset",
        workspace_dir / "dataset"
    ])

    rel_subpaths = [
        Path("PlantVillage-Dataset") / "PlantVillage-Dataset" / "raw" / "color",
        Path("PlantVillage-Dataset") / "raw" / "color",
        Path("PlantVillage-Dataset-master") / "raw" / "color",
        Path("raw") / "color",
        Path("color")
    ]

    for root in search_roots:
        if not root.exists():
            continue
        if root.is_dir() and (root / "Apple___Apple_scab").exists():
            return str(root)
        for sub in rel_subpaths:
            cand = root / sub
            if cand.exists() and cand.is_dir() and (cand / "Apple___Apple_scab").exists():
                return str(cand)
    return None

def get_file_sha256(filepath):
    """Computes SHA256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def prepare_and_split_plantvillage(raw_dir=None, processed_dir=None, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, seed=RANDOM_SEED):
    script_dir = Path(__file__).resolve().parent
    ml_service_dir = script_dir.parent

    if processed_dir is None:
        processed_dir = str(ml_service_dir / "dataset" / "processed" / "plantvillage")

    color_dir = find_raw_color_dir(raw_dir)
    if not color_dir:
        print("[-] Error: Could not locate raw PlantVillage color directory.", flush=True)
        return False

    print("===============================================================", flush=True)
    print(" PLANTVILLAGE DATASET REBUILD & STRATIFIED PER-CLASS SPLIT", flush=True)
    print("===============================================================", flush=True)
    print(f"[*] Raw Source Directory : {color_dir}", flush=True)
    print(f"[*] Target Processed Dir  : {processed_dir}", flush=True)
    print(f"[*] Target Ratios         : Train {train_ratio*100:.0f}%, Val {val_ratio*100:.0f}%, Test {test_ratio*100:.0f}%", flush=True)
    print(f"[*] Random Seed           : {seed}", flush=True)
    print("===============================================================", flush=True)

    # 1. Discover all 38 class folders in deterministic alphabetical order
    class_folders = sorted([
        d for d in os.listdir(color_dir)
        if os.path.isdir(os.path.join(color_dir, d)) and not d.startswith(".") and d != "PlantVillage-Dataset"
    ])

    num_classes = len(class_folders)
    if num_classes != 38:
        print(f"[-] Error: Expected 38 class folders in raw dataset, found {num_classes}", flush=True)

    print(f"[+] Discovered {num_classes} dataset class folders in raw source.", flush=True)

    # 2. Clean ONLY dataset/processed/plantvillage before creating splits
    print(f"[*] Safely clearing target directory: {processed_dir}", flush=True)
    clean_processed_directory(processed_dir)

    train_base = os.path.join(processed_dir, "train")
    val_base = os.path.join(processed_dir, "val")
    test_base = os.path.join(processed_dir, "test")

    os.makedirs(train_base, exist_ok=True)
    os.makedirs(val_base, exist_ok=True)
    os.makedirs(test_base, exist_ok=True)

    total_images = 0
    total_train_images = 0
    total_val_images = 0
    total_test_images = 0

    train_class_set = set()
    val_class_set = set()
    test_class_set = set()

    for idx, class_name in enumerate(class_folders):
        class_src_dir = os.path.join(color_dir, class_name)
        images = sorted([f for f in os.listdir(class_src_dir) if Path(f).suffix.lower() in VALID_EXTENSIONS])
        
        n_images = len(images)
        if n_images == 0:
            print(f"[-] Warning: Class '{class_name}' contains 0 valid images!", flush=True)
            continue

        # Group images by SHA256 content hash to prevent content duplicates across splits
        hash_to_files = {}
        for img_name in images:
            img_path = os.path.join(class_src_dir, img_name)
            h = get_file_sha256(img_path)
            if h not in hash_to_files:
                hash_to_files[h] = []
            hash_to_files[h].append(img_name)

        unique_hashes = sorted(list(hash_to_files.keys()))
        
        # Shuffle unique content hashes deterministically with seed 42
        rng = random.Random(seed + idx)
        rng.shuffle(unique_hashes)

        # Distribute hash groups across train, val, test splits aiming for 70/15/15 target image counts
        target_train = int(round(n_images * train_ratio))
        target_val = int(round(n_images * val_ratio))

        train_imgs = []
        val_imgs = []
        test_imgs = []

        curr_train_cnt = 0
        curr_val_cnt = 0

        for h in unique_hashes:
            files = hash_to_files[h]
            f_len = len(files)

            if curr_train_cnt < target_train or (curr_train_cnt + f_len <= target_train + 1 and len(val_imgs) > 0 and len(test_imgs) > 0):
                train_imgs.extend(files)
                curr_train_cnt += f_len
            elif curr_val_cnt < target_val:
                val_imgs.extend(files)
                curr_val_cnt += f_len
            else:
                test_imgs.extend(files)

        # Ensure every split gets at least 1 image group if class has enough images
        if len(val_imgs) == 0 and len(train_imgs) > 2:
            val_imgs.append(train_imgs.pop())
        if len(test_imgs) == 0 and len(train_imgs) > 2:
            test_imgs.append(train_imgs.pop())

        train_target = os.path.join(train_base, class_name)
        val_target = os.path.join(val_base, class_name)
        test_target = os.path.join(test_base, class_name)

        os.makedirs(train_target, exist_ok=True)
        os.makedirs(val_target, exist_ok=True)
        os.makedirs(test_target, exist_ok=True)

        for img in train_imgs:
            safe_copy(os.path.join(class_src_dir, img), os.path.join(train_target, img))
        for img in val_imgs:
            safe_copy(os.path.join(class_src_dir, img), os.path.join(val_target, img))
        for img in test_imgs:
            safe_copy(os.path.join(class_src_dir, img), os.path.join(test_target, img))

        if len(train_imgs) > 0:
            train_class_set.add(class_name)
        if len(val_imgs) > 0:
            val_class_set.add(class_name)
        if len(test_imgs) > 0:
            test_class_set.add(class_name)

        total_images += n_images
        total_train_images += len(train_imgs)
        total_val_images += len(val_imgs)
        total_test_images += len(test_imgs)

    # 3. Create dataset/processed/plantvillage/class_names.json with 38 alphabetical class names
    class_names_path = os.path.join(processed_dir, "class_names.json")
    with open(class_names_path, "w", encoding="utf-8") as f:
        json.dump(class_folders, f, indent=4)
    print(f"[+] Saved class_names.json to: {class_names_path}", flush=True)

    # Also save class_names.json to models/plantvillage_classifier/
    pv_model_dir = os.path.join(ml_service_dir, "models", "plantvillage_classifier")
    os.makedirs(pv_model_dir, exist_ok=True)
    with open(os.path.join(pv_model_dir, "class_names.json"), "w", encoding="utf-8") as f:
        json.dump(class_folders, f, indent=4)

    train_class_count = len(train_class_set)
    val_class_count = len(val_class_set)
    test_class_count = len(test_class_set)

    print("\n---------------------------------------------------------------", flush=True)
    print(" PREPARATION & SPLIT SUMMARY", flush=True)
    print("---------------------------------------------------------------", flush=True)
    print(f"Number of discovered classes : {num_classes}", flush=True)
    print(f"Total images                 : {total_images}", flush=True)
    print(f"Training images              : {total_train_images}", flush=True)
    print(f"Validation images            : {total_val_images}", flush=True)
    print(f"Testing images               : {total_test_images}", flush=True)
    print(f"Training class count         : {train_class_count}", flush=True)
    print(f"Validation class count       : {val_class_count}", flush=True)
    print(f"Testing class count          : {test_class_count}", flush=True)
    print("---------------------------------------------------------------", flush=True)

    # 4. Strict assertions
    assert train_class_count == 38, f"Assertion Failed: Expected 38 classes in train, got {train_class_count}"
    assert val_class_count == 38, f"Assertion Failed: Expected 38 classes in val, got {val_class_count}"
    assert test_class_count == 38, f"Assertion Failed: Expected 38 classes in test, got {test_class_count}"
    assert total_images == 54305, f"Assertion Failed: Expected 54305 total images, got {total_images}"

    print("[+] All assertions passed successfully! 38/38 classes present in train, val, and test splits.", flush=True)
    print("===============================================================\n", flush=True)
    return True

def main():
    parser = argparse.ArgumentParser(description="Prepare and split PlantVillage dataset.")
    parser.add_argument("--raw_dir", type=str, default=None,
                        help="Path to raw dataset directory")
    parser.add_argument("--processed_dir", type=str, default=None,
                        help="Target processed directory for train/val/test splits")
    args = parser.parse_args()

    success = prepare_and_split_plantvillage(args.raw_dir, args.processed_dir)
    if not success:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
