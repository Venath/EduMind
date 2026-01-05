"""
Metrics Utilities
=================
Custom evaluation metrics and reporting functions.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)


def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
) -> Dict[str, float]:
    """
    Calculate comprehensive evaluation metrics.
    
    Args:
        y_true: True labels.
        y_pred: Predicted labels.
        y_prob: Predicted probabilities for positive class.
    
    Returns:
        Dictionary of evaluation metrics.
    """
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }
    
    if y_prob is not None:
        try:
            metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob))
        except ValueError:
            # Single class in y_true
            metrics["roc_auc"] = 0.0
    
    return metrics


def confusion_matrix_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate confusion matrix with labeled values.
    
    Args:
        y_true: True labels.
        y_pred: Predicted labels.
        labels: Class labels (default: ["safe", "at_risk"]).
    
    Returns:
        Dictionary with confusion matrix data.
    """
    if labels is None:
        labels = ["safe", "at_risk"]
    
    cm = confusion_matrix(y_true, y_pred)
    
    # Extract values
    tn, fp, fn, tp = cm.ravel()
    
    return {
        "matrix": cm.tolist(),
        "labels": labels,
        "values": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        },
        "rates": {
            "true_positive_rate": float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0,
            "true_negative_rate": float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0,
            "false_positive_rate": float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0,
            "false_negative_rate": float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0,
        },
    }


def classification_report_dict(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate classification report as dictionary.
    
    Args:
        y_true: True labels.
        y_pred: Predicted labels.
        labels: Class labels.
    
    Returns:
        Classification report as dictionary.
    """
    if labels is None:
        labels = ["safe", "at_risk"]
    
    report = classification_report(
        y_true, y_pred,
        target_names=labels,
        output_dict=True,
        zero_division=0,
    )
    
    return report


def format_metrics(metrics: Dict[str, float], as_percentage: bool = True) -> str:
    """
    Format metrics for display.
    
    Args:
        metrics: Dictionary of metrics.
        as_percentage: Whether to format as percentage.
    
    Returns:
        Formatted string.
    """
    lines = []
    for key, value in metrics.items():
        if as_percentage and 0 <= value <= 1:
            lines.append(f"{key}: {value:.2%}")
        else:
            lines.append(f"{key}: {value:.4f}")
    return "\n".join(lines)


def calculate_class_weights(y: np.ndarray) -> Dict[int, float]:
    """
    Calculate class weights for imbalanced data.
    
    Args:
        y: Target labels.
    
    Returns:
        Dictionary mapping class to weight.
    """
    from collections import Counter
    
    counts = Counter(y)
    total = len(y)
    
    weights = {}
    for cls, count in counts.items():
        weights[cls] = total / (len(counts) * count)
    
    return weights


def calculate_sample_weights(y: np.ndarray) -> np.ndarray:
    """
    Calculate sample weights from class weights.
    
    Args:
        y: Target labels.
    
    Returns:
        Array of sample weights.
    """
    class_weights = calculate_class_weights(y)
    return np.array([class_weights[label] for label in y])


if __name__ == "__main__":
    # Test metrics
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1])
    y_pred = np.array([0, 0, 1, 0, 0, 1, 1, 1])
    y_prob = np.array([0.1, 0.2, 0.9, 0.4, 0.3, 0.8, 0.6, 0.7])
    
    metrics = calculate_metrics(y_true, y_pred, y_prob)
    print("Metrics:")
    print(format_metrics(metrics))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix_report(y_true, y_pred)
    print(f"  TN: {cm['values']['true_negatives']}, FP: {cm['values']['false_positives']}")
    print(f"  FN: {cm['values']['false_negatives']}, TP: {cm['values']['true_positives']}")
