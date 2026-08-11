import os
from typing import Dict, Any
import torch
import torch.nn.functional as F

from ai_core.serving.preprocessing import preprocess_xray_image
from ai_core.explainability.gradcam import GradCAMGenerator
from ai_core.explainability.heatmap import apply_heatmap_overlay

class DiseasePredictor:
    """Performs inference and Explainable AI heatmap generation with clinical metadata."""
    def __init__(self, model, device: str = "cpu", temperature: float = 1.25):
        self.model = model.to(device)
        self.device = device
        self.temperature = max(0.5, temperature)
        self.model.eval()
        self.classes = getattr(model, "classes", ["Normal", "Pneumonia", "Tuberculosis"])
        self.gradcam = GradCAMGenerator(self.model, model.get_target_layer())

    def predict_single(self, image_path: str, generate_cam: bool = True, use_tta: bool = True) -> Dict[str, Any]:
        input_tensor = preprocess_xray_image(image_path, device=self.device)
        
        with torch.no_grad():
            if use_tta:
                # Test-Time Augmentation: Standard View + Horizontal Flip
                flipped_tensor = torch.flip(input_tensor, dims=[3])
                logits_orig = self.model(input_tensor)
                logits_flip = self.model(flipped_tensor)
                logits = (logits_orig + logits_flip) / 2.0
            else:
                logits = self.model(input_tensor)

            # Apply Temperature Scaling for clinical calibration
            scaled_logits = logits / self.temperature
            probs = F.softmax(scaled_logits, dim=1).squeeze().cpu().numpy()

        top_idx = int(probs.argmax())
        top_disease = self.classes[top_idx]
        top_confidence = float(probs[top_idx])

        breakdown = [
            {"disease": self.classes[i], "confidence": round(float(probs[i]), 4)}
            for i in range(len(self.classes))
        ]

        heatmap_path = None
        if generate_cam:
            cam_tensor = self.gradcam.generate(input_tensor, class_idx=top_idx)
            base_dir = os.path.dirname(image_path)
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            heatmap_filename = f"{base_name}_heatmap.png"
            heatmap_path = os.path.join(base_dir, heatmap_filename)
            apply_heatmap_overlay(image_path, cam_tensor, heatmap_path)

        return {
            "module": "XRAY",
            "disease": top_disease,
            "prediction": top_disease,
            "confidence": round(top_confidence, 4),
            "confidence_formatted": f"{top_confidence * 100:.1f}%",
            "model": "Chest X-ray Model v1.0",
            "disclaimer": "⚠️ AI-assisted result. This system is not a replacement for professional medical diagnosis.",
            "predictions_breakdown": breakdown,
            "heatmap_generated": heatmap_path is not None,
            "heatmap_path": heatmap_path,
            "status": "completed"
        }
