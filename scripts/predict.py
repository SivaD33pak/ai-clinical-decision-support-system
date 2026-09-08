"""
AI-CDSS: Standalone Command-Line Prediction & Explainability Tool
Uses the trained 3-class DenseNet121 model and Grad-CAM engine.

Usage:
    python scripts/predict.py --image path/to/chest_xray.png
    python scripts/predict.py --image path/to/chest_xray.png --no-cam
    python scripts/predict.py --dir data/raw/chest_xray/test/TUBERCULOSIS --limit 5
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from ai_core.serving.inference_manager import inference_manager

def format_prediction_output(image_path: str, result: dict):
    print("=" * 65)
    print(f"  DIAGNOSTIC REPORT: {os.path.basename(image_path)}")
    print("=" * 65)
    print(f"  Primary Diagnosis : [ {result.get('prediction', 'Unknown').upper()} ]")
    print(f"  Confidence Score  : {result.get('confidence_formatted', 'N/A')}")
    print(f"  Model             : {result.get('model', 'DenseNet121')}")
    print("-" * 65)
    print("  Class Breakdown:")
    for item in result.get("predictions_breakdown", []):
        disease = item["disease"]
        conf = item["confidence"]
        bar_len = int(conf * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        print(f"    - {disease:<15s} : {conf*100:>5.1f}%  |{bar}|")
    
    print("-" * 65)
    if result.get("heatmap_generated") and result.get("heatmap_path"):
        print(f"  Grad-CAM Heatmap  : {result['heatmap_path']}")
    else:
        print("  Grad-CAM Heatmap  : Disabled / Not Generated")
    print(f"  Clinical Advisory : {result.get('disclaimer', '')}")
    print("=" * 65 + "\n")

async def run_single_prediction(image_path: str):
    if not os.path.exists(image_path):
        print(f"[ERROR] Image file not found: {image_path}")
        return
    res = await inference_manager.predict_xray(image_path)
    format_prediction_output(image_path, res)

async def run_batch_predictions(directory: str, limit: int = 10):
    if not os.path.isdir(directory):
        print(f"[ERROR] Directory not found: {directory}")
        return

    valid_exts = {".png", ".jpg", ".jpeg"}
    images = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.splitext(f)[1].lower() in valid_exts and not f.endswith("_heatmap.png")
    ][:limit]

    if not images:
        print(f"[WARNING] No valid image files found in {directory}")
        return

    print(f"Found {len(images)} scans to analyze in {directory}...\n")
    for img_path in images:
        res = await inference_manager.predict_xray(img_path)
        format_prediction_output(img_path, res)

def main():
    parser = argparse.ArgumentParser(description="AI-CDSS Chest X-Ray Disease Predictor")
    parser.add_argument("--image", "-i", type=str, help="Path to single Chest X-Ray image")
    parser.add_argument("--dir", "-d", type=str, help="Path to directory containing Chest X-Ray images")
    parser.add_argument("--limit", "-l", type=int, default=5, help="Max images to evaluate in directory mode (default: 5)")
    args = parser.parse_args()

    if args.image:
        asyncio.run(run_single_prediction(args.image))
    elif args.dir:
        asyncio.run(run_batch_predictions(args.dir, args.limit))
    else:
        # Default test scan if no arguments provided
        default_test = os.path.join(backend_dir, "uploads", "sample_xray.png")
        if os.path.exists(default_test):
            print("[INFO] No arguments specified. Running demonstration prediction on default sample scan:\n")
            asyncio.run(run_single_prediction(default_test))
        else:
            parser.print_help()

if __name__ == "__main__":
    main()
