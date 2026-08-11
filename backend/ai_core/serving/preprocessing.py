import torch
from PIL import Image, ImageOps
from torchvision import transforms

def letterbox_image(image: Image.Image, target_size: int = 224) -> Image.Image:
    """Preserves anatomical aspect ratio by resizing and centering on a black canvas."""
    src_w, src_h = image.size
    scale = target_size / max(src_w, src_h)
    new_w, new_h = max(1, int(src_w * scale)), max(1, int(src_h * scale))
    resized = image.resize((new_w, new_h), Image.Resampling.BILINEAR)
    
    canvas = Image.new("RGB", (target_size, target_size), (0, 0, 0))
    pad_left = (target_size - new_w) // 2
    pad_top = (target_size - new_h) // 2
    canvas.paste(resized, (pad_left, pad_top))
    return canvas

def enhance_medical_contrast(image: Image.Image) -> Image.Image:
    """Applies auto-contrast to normalize exposure variations across medical scanners."""
    gray = ImageOps.autocontrast(image.convert("L"), cutoff=1)
    return gray.convert("RGB")

INFERENCE_TRANSFORMS = transforms.Compose([
    transforms.Lambda(lambda img: enhance_medical_contrast(img)),
    transforms.Lambda(lambda img: letterbox_image(img, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def preprocess_xray_image(image_path: str, device: str = "cpu") -> torch.Tensor:
    """Preprocesses a chest X-ray image for DenseNet121 inference."""
    img = Image.open(image_path).convert("RGB")
    tensor = INFERENCE_TRANSFORMS(img).unsqueeze(0)
    return tensor.to(device)
