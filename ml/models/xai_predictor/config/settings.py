"""
XAI Predictor Configuration
===========================
Centralized configuration for the academic risk prediction model.
"""

from pathlib import Path
from typing import List, Dict, Any

# ============================================================
# PATH CONFIGURATION
# ============================================================
# All paths are relative to this config file's location
CONFIG_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CONFIG_DIR.parent

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OULAD_DIR = RAW_DATA_DIR / "OULAD"

# Artifact paths
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
MODELS_DIR = ARTIFACTS_DIR / "models"
METRICS_DIR = ARTIFACTS_DIR / "metrics"

# Legacy paths (for backward compatibility)
LEGACY_DATA_DIR = PROJECT_ROOT / "data"
LEGACY_SAVED_MODELS_DIR = PROJECT_ROOT / "saved_models"


# ============================================================
# FEATURE CONFIGURATION
# ============================================================
FEATURE_COLUMNS: List[str] = [
    "avg_grade",
    "grade_consistency",
    "grade_range",
    "num_assessments",
    "assessment_completion_rate",
    "studied_credits",
    "num_of_prev_attempts",
    "low_performance",
    "low_engagement",
    "has_previous_attempts",
]

FEATURE_DESCRIPTIONS: Dict[str, str] = {
    "avg_grade": "Average assessment score (0-100)",
    "grade_consistency": "Performance consistency (100 - std deviation)",
    "grade_range": "Score variability (max - min score)",
    "num_assessments": "Number of assessments completed",
    "assessment_completion_rate": "Assessment completion rate (0-1)",
    "studied_credits": "Course credits enrolled",
    "num_of_prev_attempts": "Number of previous course attempts",
    "low_performance": "Binary indicator: average grade < 40%",
    "low_engagement": "Binary indicator: below median assessments",
    "has_previous_attempts": "Binary indicator: has failed before",
}

TARGET_COLUMN = "is_at_risk"
CLASS_NAMES = ["Safe", "At-Risk"]


# ============================================================
# MODEL CONFIGURATION
# ============================================================
MODEL_PARAMS: Dict[str, Any] = {
    "n_estimators": 200,
    "max_depth": 5,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "objective": "binary:logistic",
    "random_state": 42,
    "use_label_encoder": False,
    "eval_metric": "logloss",
}

# Training configuration
TRAIN_TEST_SPLIT = 0.2
RANDOM_STATE = 42
USE_CLASS_WEIGHTS = True


# ============================================================
# VALIDATION THRESHOLDS
# ============================================================
MIN_ACCURACY_THRESHOLD = 0.80
MIN_PRECISION_THRESHOLD = 0.75
MIN_RECALL_THRESHOLD = 0.70
MIN_F1_THRESHOLD = 0.75

VALIDATION_THRESHOLDS = {
    "min_accuracy": MIN_ACCURACY_THRESHOLD,
    "min_precision": MIN_PRECISION_THRESHOLD,
    "min_recall": MIN_RECALL_THRESHOLD,
    "min_f1": MIN_F1_THRESHOLD,
}


# ============================================================
# RISK LEVEL THRESHOLDS
# ============================================================
RISK_THRESHOLDS = {
    "low": 0.3,      # probability < 0.3 = low risk
    "medium": 0.6,   # 0.3 <= probability < 0.6 = medium risk
    "high": 1.0,     # probability >= 0.6 = high risk
}


# ============================================================
# FILE NAMES
# ============================================================
MODEL_FILENAME = "academic_risk_model.json"
MODEL_PICKLE_FILENAME = "academic_risk_model.pkl"
METADATA_FILENAME = "model_metadata.json"
PROCESSED_DATA_FILENAME = "oulad_processed.csv"
METRICS_FILENAME = "training_metrics.json"


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_model_path(use_legacy: bool = False) -> Path:
    """Get the path to the trained model file."""
    # Primary location: artifacts/models/
    primary_path = MODELS_DIR / MODEL_FILENAME
    if primary_path.exists():
        return primary_path
    # Legacy fallback: saved_models/ (deprecated)
    if use_legacy and (LEGACY_SAVED_MODELS_DIR / MODEL_FILENAME).exists():
        return LEGACY_SAVED_MODELS_DIR / MODEL_FILENAME
    return primary_path


def get_metadata_path(use_legacy: bool = False) -> Path:
    """Get the path to the model metadata file."""
    # Primary location: artifacts/models/
    primary_path = MODELS_DIR / METADATA_FILENAME
    if primary_path.exists():
        return primary_path
    # Legacy fallback: saved_models/ (deprecated)
    if use_legacy and (LEGACY_SAVED_MODELS_DIR / METADATA_FILENAME).exists():
        return LEGACY_SAVED_MODELS_DIR / METADATA_FILENAME
    return primary_path


def get_processed_data_path(use_legacy: bool = False) -> Path:
    """Get the path to the processed data file."""
    # Primary location: data/processed/
    primary_path = PROCESSED_DATA_DIR / PROCESSED_DATA_FILENAME
    if primary_path.exists():
        return primary_path
    # Legacy fallback: data/ (root)
    if use_legacy and (LEGACY_DATA_DIR / PROCESSED_DATA_FILENAME).exists():
        return LEGACY_DATA_DIR / PROCESSED_DATA_FILENAME
    return primary_path


def ensure_directories() -> None:
    """Create all required directories if they don't exist."""
    for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, METRICS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def get_risk_level(probability: float) -> str:
    """Convert probability to risk level string."""
    if probability < RISK_THRESHOLDS["low"]:
        return "low"
    elif probability < RISK_THRESHOLDS["medium"]:
        return "medium"
    else:
        return "high"
