import torch
import torch.nn as nn
from torchvision.models import convnext_tiny, ConvNeXt_Tiny_Weights

DEFAULT_BINARY_CLASSES = ["Normal", "Tuberculosis"]
DEFAULT_TRIAGE_CLASSES = ["Normal", "Sick & Non-TB", "Tuberculosis"]

class ConvNeXtXRay(nn.Module):
    """
    State-of-the-Art ConvNeXt-Tiny customized for High-Resolution Chest X-ray Classification.
    Features 7x7 depthwise convolutions, inverted bottlenecks, and LayerNorm.
    """
    def __init__(self, num_classes: int = 3, pretrained: bool = True, classes: list = None):
        super().__init__()
        weights = ConvNeXt_Tiny_Weights.DEFAULT if pretrained else None
        self.backbone = convnext_tiny(weights=weights)
        in_features = self.backbone.classifier[2].in_features
        
        # SOTA Classification Head with LayerNorm, Dropout, and Linear Projection
        self.backbone.classifier = nn.Sequential(
            self.backbone.classifier[0],  # LayerNorm2d((768,))
            self.backbone.classifier[1],  # Flatten(start_dim=1, end_dim=-1)
            nn.Dropout(p=0.3),
            nn.Linear(in_features, num_classes)
        )
        if classes:
            self.classes = classes
        elif num_classes == 3:
            self.classes = DEFAULT_TRIAGE_CLASSES
        elif num_classes == 2:
            self.classes = DEFAULT_BINARY_CLASSES
        else:
            self.classes = [f"Class_{i}" for i in range(num_classes)]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)

    def freeze_backbone(self):
        """Freezes all feature extractor layers, training only the classification head."""
        for param in self.backbone.features.parameters():
            param.requires_grad = False

    def unfreeze_stages(self, stage_indices=(5, 6, 7)):
        """Unfreezes specific top convolutional stages for discriminative fine-tuning."""
        for idx in stage_indices:
            if idx < len(self.backbone.features):
                for param in self.backbone.features[idx].parameters():
                    param.requires_grad = True

    def unfreeze_all(self):
        """Unfreezes the entire model."""
        for param in self.parameters():
            param.requires_grad = True

    def get_target_layer(self):
        """Returns the final CNBlock in stage 3 for high-resolution Grad-CAM."""
        return self.backbone.features[-1][-1]
