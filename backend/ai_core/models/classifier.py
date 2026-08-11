import torch.nn as nn

class DiseaseClassifierHead(nn.Module):
    """Minimal classification head for DenseNet121."""
    def __init__(self, in_features: int = 1024, num_classes: int = 2, dropout_rate: float = 0.2):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(in_features, num_classes)
        )

    def forward(self, x):
        return self.fc(x)
