import os
import sys
import zipfile
import subprocess
import urllib.request
import argparse

def print_dataset_notice():
    print("===============================================================")
    print(" PlantCare AI - PlantVillage Dataset Setup Utility")
    print("===============================================================")
    print(" NOTICE:")
    print(" PlantVillage is used as an initial baseline dataset to test")
    print(" the multi-crop & disease detection pipeline.")
    print("")
    print(" IMPORTANT AGRICULTURAL LIMITATIONS:")
    print(" PlantVillage does NOT contain all Uttar Pradesh (UP) target crops.")
    print(" Crops like Sugarcane, Mustard, Chickpea, Pigeon Pea, Lentil, and Pea")
    print(" require additional verified agricultural datasets.")
    print("")
    print(" Custom/Future datasets can be placed manually in:")
    print(" ml-service/dataset/raw/<crop_name>/")
    print(" Do NOT automatically mix unknown datasets without verification.")
    print("===============================================================\n")

def download_plantvillage(target_dir):
    os.makedirs(target_dir, exist_ok=True)
    target_repo_dir = os.path.join(target_dir, "PlantVillage-Dataset")

    if os.path.exists(target_repo_dir) and any(os.scandir(target_repo_dir)):
        print(f"[+] PlantVillage dataset repository already exists at: {target_repo_dir}")
        return

    # Method 1: Git clone --depth 1 (faster and resilient against HTTP connection timeouts)
    repo_url = "https://github.com/spMohanty/PlantVillage-Dataset.git"
    print(f"[*] Attempting git clone from: {repo_url}")
    try:
        res = subprocess.run(["git", "clone", "--depth", "1", repo_url, target_repo_dir], check=True)
        if res.returncode == 0 and os.path.exists(target_repo_dir):
            print(f"[+] Successfully cloned PlantVillage repository to: {target_repo_dir}")
            return
    except Exception as e:
        print(f"[!] Git clone failed ({e}). Falling back to zip download...")

    # Method 2: Direct zip download fallback
    zip_path = os.path.join(target_dir, "plantvillage.zip")
    url = "https://github.com/spMohanty/PlantVillage-Dataset/archive/refs/heads/master.zip"
    
    print(f"[*] Downloading PlantVillage dataset zip from: {url}")
    print(f"[*] Target location: {zip_path}")
    
    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = downloaded * 100 / total_size
            sys.stdout.write(f"\rDownloading: {percent:.1f}% ({downloaded / (1024*1024):.1f} MB)")
            sys.stdout.flush()

    try:
        urllib.request.urlretrieve(url, zip_path, reporthook=report_progress)
        print("\n[+] Download complete!")
        
        print("[*] Extracting archive...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        print("[+] Extraction complete!")
        
        extracted_master = os.path.join(target_dir, "PlantVillage-Dataset-master")
        if os.path.exists(extracted_master) and not os.path.exists(target_repo_dir):
            os.rename(extracted_master, target_repo_dir)

        if os.path.exists(zip_path):
            os.remove(zip_path)
            
    except Exception as e:
        print(f"\n[-] Error downloading PlantVillage dataset: {e}")
        print("[!] You can manually download the dataset zip from:")
        print("    https://github.com/spMohanty/PlantVillage-Dataset")
        print(f"    and extract its contents into: {target_dir}")

def main():
    parser = argparse.ArgumentParser(description="Download PlantVillage baseline dataset.")
    parser.add_argument("--target_dir", type=str, default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset", "raw"),
                        help="Target directory for raw dataset")
    args = parser.parse_args()

    print_dataset_notice()
    download_plantvillage(args.target_dir)

if __name__ == "__main__":
    main()
