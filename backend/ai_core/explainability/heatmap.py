import numpy as np
from PIL import Image
import torch

def _jet_colormap(val: np.ndarray) -> np.ndarray:
    """Vectorized Jet colormap conversion (pure numpy, zero dependency)."""
    four_val = 4 * val
    r = np.clip(np.minimum(four_val - 1.5, -four_val + 4.5), 0, 1)
    g = np.clip(np.minimum(four_val - 0.5, -four_val + 3.5), 0, 1)
    b = np.clip(np.minimum(four_val + 0.5, -four_val + 2.5), 0, 1)
    return (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)

def apply_heatmap_overlay(
    original_image_path: str,
    cam_tensor: torch.Tensor,
    output_path: str,
    max_alpha: float = 0.65,
    threshold: float = 0.20
) -> str:
    """
    Overlays Grad-CAM attention heatmap onto the original chest X-ray image with
    medical-grade smooth alpha transparency:
    - Low background activations (< threshold) remain completely transparent so normal
      lung tissue and dark background are NOT falsely tinted.
    - Pathological focal hotspots smoothly transition from yellow to intense red.
    - Outer margins and corner triangles are masked to eliminate edge artifacts.
    """
    orig = Image.open(original_image_path).convert("RGBA")
    w, h = orig.size

    cam_np = cam_tensor.detach().cpu().numpy() if isinstance(cam_tensor, torch.Tensor) else np.array(cam_tensor)

    # Bilinear resize CAM to match original image dimensions
    cam_resized = Image.fromarray((cam_np * 255).astype(np.uint8)).resize((w, h), Image.Resampling.BILINEAR)
    cam_norm = np.array(cam_resized, dtype=np.float32) / 255.0

    # Build anatomical thoracic border mask to zero out corner/margin artifacts
    mask = np.ones((h, w), dtype=np.float32)
    m_w, m_h = max(1, int(w * 0.05)), max(1, int(h * 0.05))
    mask[:m_h, :] = 0.0
    mask[-m_h:, :] = 0.0
    mask[:, :m_w] = 0.0
    mask[:, -m_w:] = 0.0

    # Smooth corner triangles
    c_w = max(1, int(w * 0.12))
    c_h = max(1, int(h * 0.12))
    for y in range(c_h):
        for x in range(c_w):
            if (x / c_w) + (y / c_h) < 1.0:
                mask[y, x] = 0.0
                mask[y, w - 1 - x] = 0.0
                mask[h - 1 - y, x] = 0.0
                mask[h - 1 - y, w - 1 - x] = 0.0

    cam_clean = cam_norm * mask

    # Alpha thresholding: transparent below threshold, scaling up to max_alpha
    alpha = np.clip((cam_clean - threshold) / max(1.0 - threshold, 1e-6), 0.0, 1.0) * max_alpha
    alpha_uint8 = (alpha * 255).astype(np.uint8)

    # Colorize heatmap
    colored_rgb = _jet_colormap(cam_clean)
    heatmap_rgba = np.dstack([colored_rgb, alpha_uint8])
    heatmap_img = Image.fromarray(heatmap_rgba, mode="RGBA")

    # Alpha composite over original image
    blended = Image.alpha_composite(orig, heatmap_img)
    blended.convert("RGB").save(output_path, quality=94)
    return output_path
