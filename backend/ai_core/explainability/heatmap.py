import numpy as np
from PIL import Image
import torch

def _jet_colormap(val: np.ndarray) -> np.ndarray:
    """Vectorized Jet colormap conversion (pure numpy, zero dependency)."""
    # val is in [0, 1]
    four_val = 4 * val
    r = np.clip(np.minimum(four_val - 1.5, -four_val + 4.5), 0, 1)
    g = np.clip(np.minimum(four_val - 0.5, -four_val + 3.5), 0, 1)
    b = np.clip(np.minimum(four_val + 0.5, -four_val + 2.5), 0, 1)
    return (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)

def apply_heatmap_overlay(original_image_path: str, cam_tensor: torch.Tensor, output_path: str, alpha: float = 0.45) -> str:
    """
    Overlays Grad-CAM attention heatmap onto the original chest X-ray image and saves to disk.
    """
    orig = Image.open(original_image_path).convert("RGB")
    w, h = orig.size

    cam_np = cam_tensor.detach().numpy() if isinstance(cam_tensor, torch.Tensor) else np.array(cam_tensor)
    cam_resized = Image.fromarray((cam_np * 255).astype(np.uint8)).resize((w, h), Image.Resampling.BILINEAR)
    cam_norm = np.array(cam_resized) / 255.0

    colored_heatmap = Image.fromarray(_jet_colormap(cam_norm))
    blended = Image.blend(orig, colored_heatmap, alpha=alpha)
    blended.save(output_path, quality=92)
    return output_path
