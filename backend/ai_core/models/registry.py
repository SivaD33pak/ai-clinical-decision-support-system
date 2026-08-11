from typing import Dict, Any, Optional
from app.core.logging import logger

class ModelRegistry:
    """Registry holding instantiated PyTorch models for inference."""
    def __init__(self):
        self._models: Dict[str, Any] = {}

    def register(self, name: str, model_instance: Any):
        self._models[name] = model_instance
        logger.info(f"Model '{name}' registered in ModelRegistry.")

    def get(self, name: str) -> Optional[Any]:
        return self._models.get(name)

    def has(self, name: str) -> bool:
        return name in self._models

model_registry = ModelRegistry()
