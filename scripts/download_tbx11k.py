"""
TBX11K Dataset Downloader & Extractor
IEEE TPAMI 2023 / CVPR 2020 Oral: 'Revisiting Computer-Aided Tuberculosis Diagnosis'
Google Drive File ID: 1r-oNYTPiPCOUzSjChjCIYTdkjBTugqxR
"""

import os
import sys
import zipfile
import gdown
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
TARGET_DIR = DATA_DIR / "TBX11K"
ZIP_PATH = DATA_DIR / "TBX11K.zip"
GDRIVE_ID = "1r-oNYTPiPCOUzSjChjCIYTdkjBTugqxR"

def download_and_extract():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    print(f"=== TBX11K Dataset Downloader ===")
    print(f"Destination: {TARGET_DIR}")
    print(f"Zip Location: {ZIP_PATH}")

    # Check if already extracted
    imgs_dir = TARGET_DIR / "imgs"
    if imgs_dir.exists() and len(list(imgs_dir.glob("*.png"))) > 1000:
        print(f"[OK] Dataset already extracted at {TARGET_DIR} with {len(list(imgs_dir.glob('*.png')))} images.")
        return

    # Check if zip exists
    if not ZIP_PATH.exists() or ZIP_PATH.stat().st_size < 1000000:
        print(f"Downloading TBX11K.zip from Google Drive (ID: {GDRIVE_ID})...")
        try:
            output = gdown.download(
                id=GDRIVE_ID,
                output=str(ZIP_PATH),
                quiet=False,
                resume=True
            )
            if not output or not ZIP_PATH.exists():
                raise RuntimeError("Download failed to produce output file.")
        except Exception as e:
            print(f"Error during download: {e}")
            sys.exit(1)
    else:
        print(f"[OK] Found existing TBX11K.zip ({ZIP_PATH.stat().st_size / (1024**3):.2f} GB). Skipping download.")

    print(f"Extracting {ZIP_PATH} to {TARGET_DIR}...")
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            namelist = zip_ref.namelist()
            print(f"Archive contains {len(namelist)} items. Extracting...")
            zip_ref.extractall(DATA_DIR)
        print("[SUCCESS] Extraction completed!")
    except Exception as e:
        print(f"Extraction failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_and_extract()
