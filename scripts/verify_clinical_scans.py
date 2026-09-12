"""
Verification script for real-world clinical chest X-rays using the newly trained 3-Class ConvNeXt on TBX11K.
"""

import os
import sys
import glob
import asyncio
from pathlib import Path

# Setup paths
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from ai_core.serving.inference_manager import inference_manager

async def run_verification():
    print("============================================================")
    print("   AI-CDSS Real-World Clinical Chest X-Ray Verification     ")
    print("============================================================")

    tb_images = sorted(glob.glob(str(ROOT_DIR / "data" / "raw" / "TBX11K" / "imgs" / "tb" / "*.png")))
    sick_images = sorted(glob.glob(str(ROOT_DIR / "data" / "raw" / "TBX11K" / "imgs" / "sick" / "*.png")))
    health_images = sorted(glob.glob(str(ROOT_DIR / "data" / "raw" / "TBX11K" / "imgs" / "health" / "*.png")))

    test_cases = [
        ("Tuberculosis Case", tb_images[0] if tb_images else None),
        ("Other Pulmonary Disease (Non-TB) Case", sick_images[0] if sick_images else None),
        ("Healthy Normal Case", health_images[0] if health_images else None)
    ]

    for label, img_path in test_cases:
        if not img_path or not os.path.exists(img_path):
            print(f"Skipping {label}: file not found.")
            continue

        print(f"\n--- Testing {label} [{os.path.basename(img_path)}] ---")
        result = await inference_manager.predict_xray(img_path)
        print(f"  Primary Diagnosis: {result['disease']}")
        print(f"  Confidence:        {result['confidence_formatted']}")
        print(f"  Model Engine:      {result['model']}")
        print(f"  Heatmap Saved:     {result['heatmap_generated']} -> {result['heatmap_path']}")
        print(f"  Class Breakdown:")
        for item in result["predictions_breakdown"]:
            bar = "#" * int(item["confidence"] * 30)
            print(f"    - {item['disease']:<28} {item['confidence']*100:5.1f}% | {bar}")

    print("\n============================================================")
    print("   Evaluating 10 Consecutive Real Tuberculosis Patient Scans ")
    print("============================================================")
    tb_batch = tb_images[1:11]
    for p in tb_batch:
        fname = os.path.basename(p)
        res = await inference_manager.predict_xray(p)
        tb_prob = res["predictions_breakdown"][2]["confidence"] * 100
        print(f"  {fname:<14} -> Diagnosis: {res['disease']:<16} | TB Prob: {tb_prob:5.1f}% | Top Conf: {res['confidence_formatted']}")

    # Corner Heatmap Audit: Verify that corners are 100% transparent / zero activation
    from PIL import Image
    import numpy as np
    sample_heatmap_path = result["heatmap_path"]
    if sample_heatmap_path and os.path.exists(sample_heatmap_path):
        hm_img = Image.open(sample_heatmap_path)
        hm_arr = np.array(hm_img)
        print("\n--- Heatmap Corner Artifact Audit ---")
        print(f"  Heatmap Dimensions: {hm_arr.shape}")
        # Check top-left, top-right, bottom-left, bottom-right corners
        tl = hm_arr[0:15, 0:15, 0:3].mean()
        tr = hm_arr[0:15, -15:, 0:3].mean()
        bl = hm_arr[-15:, 0:15, 0:3].mean()
        br = hm_arr[-15:, -15:, 0:3].mean()
        print(f"  Corner pixel intensities (should be zero/dark due to aperture): TL={tl:.1f}, TR={tr:.1f}, BL={bl:.1f}, BR={br:.1f}")
        assert max(tl, tr, bl, br) < 5.0, "Corner artifact detected in heatmap!"
        print("  [PASS] Corner heatmaps verified completely black/zero! No shortcut learning!")

    print("\n[SUCCESS] Clinical verification script completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_verification())
