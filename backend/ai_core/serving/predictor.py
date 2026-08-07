# Single & Batch Inference Predictor

class DiseasePredictor:
    """Executes single image or batch inference using loaded PyTorch weights."""
    def __init__(self, model, device="cpu"):
        self.model = model
        self.device = device

    async def predict_single(self, image_path: str):
        pass
