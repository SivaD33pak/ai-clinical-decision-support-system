from typing import Dict, Any, List
import numpy as np

def calculate_clinical_metrics(y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
    """
    Computes key clinical metrics: Accuracy, Precision, Sensitivity/Recall, Specificity, F1-Score.
    """
    yt = np.array(y_true)
    yp = np.array(y_pred)

    tp = np.sum((yt == 1) & (yp == 1))
    tn = np.sum((yt == 0) & (yp == 0))
    fp = np.sum((yt == 0) & (yp == 1))
    fn = np.sum((yt == 1) & (yp == 0))

    accuracy = (tp + tn) / max(len(yt), 1)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1) # Sensitivity
    specificity = tn / max(tn + fp, 1)
    f1 = 2 * (precision * recall) / max(precision + recall, 1e-7)

    return {
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "sensitivity_recall": round(float(recall), 4),
        "specificity": round(float(specificity), 4),
        "f1_score": round(float(f1), 4),
        "tp": int(tp),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn)
    }
