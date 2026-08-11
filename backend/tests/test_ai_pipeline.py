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

from ai_core.models.densenet import DenseNet121XRay
from ai_core.explainability.gradcam import GradCAMGenerator
from ai_core.explainability.heatmap import apply_heatmap_overlay
from ai_core.serving.predictor import DiseasePredictor
from ai_core.evaluation.metrics import calculate_clinical_metrics

def test_ai_pipeline():
    print("--- 1. Testing 3-Class DenseNet121 Architecture & Forward Pass ---")
    model = DenseNet121XRay(num_classes=3, pretrained=False)
    dummy_input = torch.randn(2, 3, 224, 224)
    logits = model(dummy_input)
    assert logits.shape == (2, 3), f"Expected logits (2, 3), got {logits.shape}"
    print("[PASS] Forward pass shape:", logits.shape)

    print("\n--- 2. Testing Grad-CAM Heatmap Generation ---")
    gradcam = GradCAMGenerator(model, model.get_target_layer())
    single_input = torch.randn(1, 3, 224, 224)
    cam = gradcam.generate(single_input, class_idx=0)
    assert cam.shape == (224, 224), f"Expected CAM (224, 224), got {cam.shape}"
    assert 0.0 <= float(cam.min()) and float(cam.max()) <= 1.0, "CAM values not in [0, 1]"
    print("[PASS] Grad-CAM output shape:", cam.shape, "min:", float(cam.min()), "max:", float(cam.max()))

    print("\n--- 3. Testing Heatmap Overlay Rendering ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        test_img_path = os.path.join(tmpdir, "test_xray.png")
        out_overlay_path = os.path.join(tmpdir, "test_xray_heatmap.png")
        Image.new("RGB", (300, 300), color=(128, 128, 128)).save(test_img_path)
        
        apply_heatmap_overlay(test_img_path, cam, out_overlay_path)
        assert os.path.exists(out_overlay_path), "Overlay image was not saved"
        print("[PASS] Heatmap overlay successfully saved to:", out_overlay_path)

        print("\n--- 4. Testing 3-Class DiseasePredictor with Clinical Result Formatting ---")
        predictor = DiseasePredictor(model, device="cpu")
        result = predictor.predict_single(test_img_path, generate_cam=True)
        assert "disease" in result
        assert "prediction" in result
        assert "confidence" in result
        assert "confidence_formatted" in result
        assert "model" in result
        assert "disclaimer" in result
        assert len(result["predictions_breakdown"]) == 3
        assert result["heatmap_generated"] is True
        assert os.path.exists(result["heatmap_path"])
        print("[PASS] Analysis Result:")
        print(f"  Prediction: {result['prediction']}")
        print(f"  Confidence: {result['confidence_formatted']}")
        print(f"  Model: {result['model']}")
        print(f"  Disclaimer: {result['disclaimer']}")

    print("\n--- 5. Testing Clinical Evaluation Metrics ---")
    y_true = [1, 1, 0, 0, 1]
    y_pred = [1, 0, 0, 0, 1]
    metrics = calculate_clinical_metrics(y_true, y_pred)
    assert metrics["accuracy"] == 0.8
    assert metrics["precision"] == 1.0
    assert metrics["specificity"] == 1.0
    print("[PASS] Clinical metrics:", metrics)

    print("\n[SUCCESS] ALL 3-CLASS AI PIPELINE & GRAD-CAM TESTS PASSED CLEANLY!")

if __name__ == "__main__":
    test_ai_pipeline()
