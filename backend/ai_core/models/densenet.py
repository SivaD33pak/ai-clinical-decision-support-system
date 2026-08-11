import torch
import torch.nn as nn
from torchvision.models import densenet121, DenseNet121_Weights
from ai_core.models.classifier import DiseaseClassifierHead

DEFAULT_CLASSES = ["Normal", "Pneumonia", "Tuberculosis"]

class DenseNet121XRay(nn.Module):
    """DenseNet121 customized for Chest X-ray classification (Normal, Pneumonia, Tuberculosis)."""
    def __init__(self, num_classes: int = 3, pretrained: bool = True, classes=None):
        super().__init__()
        weights = DenseNet121_Weights.DEFAULT if pretrained else None
        self.backbone = densenet121(weights=weights)
        in_features = self.backbone.classifier.in_features
        self.backbone.classifier = DiseaseClassifierHead(in_features, num_classes)
        self.classes = classes or DEFAULT_CLASSES[:num_classes]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)

    def freeze_backbone(self):
        for param in self.backbone.features.parameters():
            param.requires_grad = False

    def unfreeze_all(self):
        for param in self.parameters():
            param.requires_grad = True

    def get_target_layer(self):
        # Last convolutional feature layer for Grad-CAM
        return self.backbone.features.norm5
