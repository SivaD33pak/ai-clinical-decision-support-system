import os
import torch

def save_checkpoint(model: torch.nn.Module, filepath: str, **metadata):
    """Saves model weights and optional metadata to disk."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    payload = {
        "model_state_dict": model.state_dict(),
        "classes": getattr(model, "classes", ["Normal", "Pneumonia"]),
        **metadata
    }
    torch.save(payload, filepath)

def load_checkpoint(model: torch.nn.Module, filepath: str, device: str = "cpu"):
    """Loads checkpoint into an existing model instance."""
    checkpoint = torch.load(filepath, map_location=device)
    state_dict = checkpoint["model_state_dict"] if "model_state_dict" in checkpoint else checkpoint
    model.load_state_dict(state_dict, strict=False)
    return checkpoint
