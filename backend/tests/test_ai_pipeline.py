import os
import sys
import tempfile
from pathlib import Path
from PIL import Image
import torch

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure backend root is in sys.path
backend_root = Path(__file__).parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from ai_core.models.convnext import ConvNeXtXRay
from ai_core.models.densenet import DenseNet121XRay
from ai_core.explainability.gradcam import GradCAMGenerator
from ai_core.explainability.heatmap import apply_heatmap_overlay
from ai_core.serving.predictor import DiseasePredictor
from ai_core.evaluation.metrics import calculate_clinical_metrics

def test_ai_pipeline():
    print("--- 1. Testing SOTA ConvNeXtXRay Architecture & Forward Pass (384x384) ---")
    model = ConvNeXtXRay(num_classes=2, pretrained=False, classes=["Normal", "Tuberculosis"])
    dummy_input = torch.randn(2, 3, 384, 384)
    logits = model(dummy_input)
    assert logits.shape == (2, 2), f"Expected logits (2, 2), got {logits.shape}"
    print("[PASS] ConvNeXt forward pass shape:", logits.shape)

    print("\n--- 2. Testing ConvNeXt Grad-CAM Heatmap Generation ---")
    target_layer = model.get_target_layer()
    gradcam = GradCAMGenerator(model, target_layer)
    single_input = torch.randn(1, 3, 384, 384)
    cam = gradcam.generate(single_input, class_idx=1)
    assert cam.shape == (384, 384), f"Expected CAM (384, 384), got {cam.shape}"
    assert 0.0 <= float(cam.min()) and float(cam.max()) <= 1.0, "CAM values not in [0, 1]"
    print("[PASS] Grad-CAM output shape:", cam.shape, "min:", float(cam.min()), "max:", float(cam.max()))

    print("\n--- 3. Testing Heatmap Overlay Rendering ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        test_img_path = os.path.join(tmpdir, "test_xray.png")
        out_overlay_path = os.path.join(tmpdir, "test_xray_heatmap.png")
        Image.new("RGB", (400, 400), color=(128, 128, 128)).save(test_img_path)
        
        apply_heatmap_overlay(test_img_path, cam, out_overlay_path)
        assert os.path.exists(out_overlay_path), "Overlay image was not saved"
        print("[PASS] Heatmap overlay successfully saved to:", out_overlay_path)

        print("\n--- 4. Testing DiseasePredictor with Tuberculosis Clinical Output ---")
        predictor = DiseasePredictor(model, device="cpu")
        result = predictor.predict_single(test_img_path, generate_cam=True)
        assert "disease" in result
        assert "prediction" in result
        assert "confidence" in result
        assert "confidence_formatted" in result
        assert "model" in result
        assert "disclaimer" in result
        assert len(result["predictions_breakdown"]) == 2
        assert result["heatmap_generated"] is True
        assert os.path.exists(result["heatmap_path"])
        print("[PASS] SOTA Analysis Result:")
        print(f"  Prediction: {result['prediction']}")
        print(f"  Confidence: {result['confidence_formatted']}")
        print(f"  Model: {result['model']}")
        print(f"  Disclaimer: {result['disclaimer']}")
        print(f"  Breakdown: {result['predictions_breakdown']}")

    print("\n--- 5. Testing Clinical Evaluation Metrics ---")
    y_true = [1, 1, 0, 0, 1]
    y_pred = [1, 0, 0, 0, 1]
    metrics = calculate_clinical_metrics(y_true, y_pred)
    assert metrics["accuracy"] == 0.8
    assert metrics["precision"] == 1.0
    assert metrics["specificity"] == 1.0
    print("[PASS] Clinical metrics:", metrics)

    print("\n--- 6. Testing Clinical Thoracic Filter & Anti-Shortcut Corner Mask ---")
    from ai_core.serving.preprocessing import apply_clinical_thoracic_filter
    import numpy as np
    raw_dummy = Image.new("RGB", (512, 512), color=(220, 220, 220))  # Simulates bright film borders
    filtered = apply_clinical_thoracic_filter(raw_dummy, target_size=384)
    arr = np.array(filtered)
    assert arr.shape == (384, 384, 3), f"Expected shape (384, 384, 3), got {arr.shape}"
    assert arr[0, 0, 0] == 0 and arr[0, -1, 0] == 0 and arr[-1, 0, 0] == 0 and arr[-1, -1, 0] == 0
    print("[PASS] Thoracic filter zeroes corner shortcuts successfully.")
    print("\n--- 7. Testing 3-Class ConvNeXt & TBX11K Triage Integration ---")
    model_3cls = ConvNeXtXRay(num_classes=3, pretrained=False)
    assert model_3cls.classes == ["Normal", "Sick & Non-TB", "Tuberculosis"]
    logits_3cls = model_3cls(torch.randn(2, 3, 384, 384))
    assert logits_3cls.shape == (2, 3), f"Expected (2, 3), got {logits_3cls.shape}"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_img_path = os.path.join(tmpdir, "test_3cls.png")
        Image.new("RGB", (384, 384), color=(100, 100, 100)).save(test_img_path)
        predictor_3cls = DiseasePredictor(model_3cls, device="cpu")
        res_3cls = predictor_3cls.predict_single(test_img_path, generate_cam=False)
        assert len(res_3cls["predictions_breakdown"]) == 3
        assert res_3cls["disease"] in ["Normal", "Sick & Non-TB", "Tuberculosis"]
        print("[PASS] 3-Class ConvNeXt output breakdown:", res_3cls["predictions_breakdown"])

    from ai_core.data.tbx11k_dataset import TBX11KDataset
    data_dir = os.path.join(backend_root.parent, "data", "raw", "TBX11K")
    if os.path.exists(data_dir):
        val_ds = TBX11KDataset(data_dir, split="val", return_meta=True)
        assert len(val_ds) > 0
        img_t, lbl, meta = val_ds[0]
        assert img_t.shape == (3, 384, 384)
        assert lbl in [0, 1, 2]
        print(f"[PASS] Successfully loaded TBX11K sample: {meta['filename']} -> Class {lbl} ({meta['class_name']})")

    print("\n[SUCCESS] ALL SOTA TUBERCULOSIS AI PIPELINE & GRAD-CAM TESTS PASSED CLEANLY!")

if __name__ == "__main__":
    test_ai_pipeline()

