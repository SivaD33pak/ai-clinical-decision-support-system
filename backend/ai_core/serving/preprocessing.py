import torch
from PIL import Image, ImageOps, ImageDraw
from torchvision import transforms

DEFAULT_IMAGE_SIZE = 384

def apply_clinical_thoracic_filter(image: Image.Image, target_size: int = DEFAULT_IMAGE_SIZE) -> Image.Image:
    """
    Clinical Thoracic Preprocessing Pipeline:
    1. Grayscale luminance conversion (standardizes 1-channel / 3-channel input disparity).
    2. Perimeter margin trimming: removes outer 6% perimeter containing film digitizer borders,
       scanner frame lines, and corner text / lead markers ('L', 'R').
    3. Adaptive lung-field histogram equalization: normalizes exposure on actual thoracic tissue.
    4. Aspect-ratio preserving letterboxing to target_size.
    5. Corner blackout aperture: zeroes out the 4 outer corner triangles, guaranteeing
       zero feature variance across classes and preventing convolutional corner shortcuts.
    """
    gray = image.convert("L")
    w, h = gray.size
    
    # 1. Trim outer 6% perimeter (scanner edges, collimator lines, text stamps)
    crop_x = int(w * 0.06)
    crop_y = int(h * 0.06)
    gray = gray.crop((crop_x, crop_y, max(crop_x + 1, w - crop_x), max(crop_y + 1, h - crop_y)))
    
    # 2. Contrast enhancement on the thoracic cavity
    eq = ImageOps.equalize(gray)
    auto = ImageOps.autocontrast(gray, cutoff=1)
    blended = Image.blend(auto, eq, alpha=0.5)
    
    # 3. Aspect-ratio preserving letterbox
    scale = target_size / max(blended.size)
    nw, nh = max(1, int(blended.size[0] * scale)), max(1, int(blended.size[1] * scale))
    resized = blended.resize((nw, nh), Image.Resampling.BILINEAR)
    
    canvas = Image.new("L", (target_size, target_size), 0)
    pad_l = (target_size - nw) // 2
    pad_t = (target_size - nh) // 2
    canvas.paste(resized, (pad_l, pad_t))
    
    # 4. Zero out 4 corner triangles (corner blackout mask)
    draw = ImageDraw.Draw(canvas)
    c_size = int(target_size * 0.12)
    # Top-Left, Top-Right, Bottom-Left, Bottom-Right
    draw.polygon([(0, 0), (c_size, 0), (0, c_size)], fill=0)
    draw.polygon([(target_size, 0), (target_size - c_size, 0), (target_size, c_size)], fill=0)
    draw.polygon([(0, target_size), (c_size, target_size), (0, target_size - c_size)], fill=0)
    draw.polygon([(target_size, target_size), (target_size - c_size, target_size), (target_size, target_size - c_size)], fill=0)
    
    return canvas.convert("RGB")

def get_inference_transforms(target_size: int = DEFAULT_IMAGE_SIZE):
    return transforms.Compose([
        transforms.Lambda(lambda img: apply_clinical_thoracic_filter(img, target_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

INFERENCE_TRANSFORMS = get_inference_transforms(DEFAULT_IMAGE_SIZE)

def preprocess_xray_image(image_path: str, device: str = "cpu", target_size: int = DEFAULT_IMAGE_SIZE) -> torch.Tensor:
    """Preprocesses a chest X-ray image for SOTA ConvNeXt/DenseNet inference."""
    img = Image.open(image_path)
    tfm = INFERENCE_TRANSFORMS if target_size == DEFAULT_IMAGE_SIZE else get_inference_transforms(target_size)
    tensor = tfm(img).unsqueeze(0)
    return tensor.to(device)
