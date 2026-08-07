# Custom Classification Heads for CDSS Models

class DiseaseClassifierHead:
    """Classification head with dropout and linear layer for disease prediction."""
    def __init__(self, in_features=1024, num_classes=4, dropout_rate=0.2):
        self.in_features = in_features
        self.num_classes = num_classes
        self.dropout_rate = dropout_rate
