import torch
from PIL import Image
from torchvision import transforms

INFERENCE_TRANSFORMS = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def preprocess_xray_image(image_path: str, device: str = "cpu") -> torch.Tensor:
    """Preprocesses a chest X-ray image for DenseNet121 inference."""
    img = Image.open(image_path).convert("RGB")
    tensor = INFERENCE_TRANSFORMS(img).unsqueeze(0)
    return tensor.to(device)
