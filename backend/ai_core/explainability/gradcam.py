import torch
import torch.nn.functional as F

class GradCAMGenerator:
    """Computes Gradient-weighted Class Activation Mapping (Grad-CAM)."""
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.activations = None
        self.gradients = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output
            if output.requires_grad:
                output.register_hook(self._save_gradient)

        self.target_layer.register_forward_hook(forward_hook)

    def _save_gradient(self, grad):
        self.gradients = grad.detach()

    def generate(self, input_tensor: torch.Tensor, class_idx: int = None) -> torch.Tensor:
        """
        Generates a 2D normalized Grad-CAM heatmap tensor (H, W) for class_idx.
        """
        self.model.eval()
        # Enable gradients for activation tracking
        input_tensor = input_tensor.clone()
        output = self.model(input_tensor)
        
        if class_idx is None:
            class_idx = output.argmax(dim=1).item()

        self.model.zero_grad()
        score = output[0, class_idx]
        score.backward(retain_graph=True)

        if self.gradients is None or self.activations is None:
            return torch.zeros((input_tensor.shape[2], input_tensor.shape[3]))

        # Global average pool the gradients
        weights = torch.mean(self.gradients, dim=(2, 3), keepdim=True)
        cam = torch.sum(weights * self.activations.detach(), dim=1, keepdim=True)
        cam = F.relu(cam)

        # Normalize between 0 and 1
        cam_min, cam_max = cam.min(), cam.max()
        if cam_max > cam_min:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = torch.zeros_like(cam)

        # Upsample to input spatial dimensions
        cam = F.interpolate(cam, size=(input_tensor.shape[2], input_tensor.shape[3]), mode="bilinear", align_corners=False)
        return cam.squeeze().cpu()
