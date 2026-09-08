import torch
from PIL import Image, ImageOps
from torchvision import transforms

DEFAULT_IMAGE_SIZE = 384

def letterbox_image(image: Image.Image, target_size: int = DEFAULT_IMAGE_SIZE) -> Image.Image:
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
    """
    Applies medical-grade adaptive histogram equalization and contrast normalization
    to standardize exposure variations across different X-ray scanners.
    """
    gray = image.convert("L")
    eq = ImageOps.equalize(gray)
    auto = ImageOps.autocontrast(gray, cutoff=1)
    blended = Image.blend(auto, eq, alpha=0.5)
    return blended.convert("RGB")

def get_inference_transforms(target_size: int = DEFAULT_IMAGE_SIZE):
    return transforms.Compose([
        transforms.Lambda(lambda img: enhance_medical_contrast(img)),
        transforms.Lambda(lambda img: letterbox_image(img, target_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

INFERENCE_TRANSFORMS = get_inference_transforms(DEFAULT_IMAGE_SIZE)

def preprocess_xray_image(image_path: str, device: str = "cpu", target_size: int = DEFAULT_IMAGE_SIZE) -> torch.Tensor:
    """Preprocesses a chest X-ray image for SOTA ConvNeXt/DenseNet inference."""
    img = Image.open(image_path).convert("RGB")
    tfm = INFERENCE_TRANSFORMS if target_size == DEFAULT_IMAGE_SIZE else get_inference_transforms(target_size)
    tensor = tfm(img).unsqueeze(0)
    return tensor.to(device)
