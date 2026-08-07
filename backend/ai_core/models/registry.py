from typing import Dict, Any, Optional
from app.core.logging import logger

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, Any] = {}

    def register_model(self, model_name: str, model_instance: Any):
        self._models[model_name] = model_instance
        logger.info(f"AI Model '{model_name}' registered successfully in AI Core Model Registry.")

    def get_model(self, model_name: str) -> Optional[Any]:
        return self._models.get(model_name)

    def is_registered(self, model_name: str) -> bool:
        return model_name in self._models

model_registry = ModelRegistry()
