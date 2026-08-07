# Training Callbacks (Early Stopping, Metric Tracker)

class EarlyStopping:
    """Early stopping callback to halt training when validation loss stops improving."""
    def __init__(self, patience=5, min_delta=1e-4):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = None
        self.counter = 0
        self.early_stop = False
