# DenseNet121 Architecture for Chest X-ray Classification

class DenseNet121XRay:
    """DenseNet121 model wrapper customized for medical image classification."""
    def __init__(self, num_classes=4, pretrained=True):
        self.num_classes = num_classes
        self.pretrained = pretrained
