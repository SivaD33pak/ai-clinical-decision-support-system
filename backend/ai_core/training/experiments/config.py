# Training Experiment Hyperparameter Configurations

class ExperimentConfig:
    BATCH_SIZE: int = 32
    EPOCHS: int = 50
    LEARNING_RATE: float = 1e-4
    WEIGHT_DECAY: float = 1e-5
    IMAGE_SIZE: tuple = (224, 224)
    NUM_CLASSES: int = 4
