"""
XAI Predictor Configuration Package
"""

from config.settings import (
    # Paths
    PROJECT_ROOT,
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    OULAD_DIR,
    ARTIFACTS_DIR,
    MODELS_DIR,
    METRICS_DIR,
    # Features
    FEATURE_COLUMNS,
    FEATURE_DESCRIPTIONS,
    TARGET_COLUMN,
    CLASS_NAMES,
    # Model
    MODEL_PARAMS,
    TRAIN_TEST_SPLIT,
    RANDOM_STATE,
    # Thresholds
    MIN_ACCURACY_THRESHOLD,
    RISK_THRESHOLDS,
    # Helpers
    get_model_path,
    get_metadata_path,
    get_processed_data_path,
    ensure_directories,
    get_risk_level,
)

__all__ = [
    "PROJECT_ROOT",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "PROCESSED_DATA_DIR",
    "OULAD_DIR",
    "ARTIFACTS_DIR",
    "MODELS_DIR",
    "METRICS_DIR",
    "FEATURE_COLUMNS",
    "FEATURE_DESCRIPTIONS",
    "TARGET_COLUMN",
    "CLASS_NAMES",
    "MODEL_PARAMS",
    "TRAIN_TEST_SPLIT",
    "RANDOM_STATE",
    "MIN_ACCURACY_THRESHOLD",
    "RISK_THRESHOLDS",
    "get_model_path",
    "get_metadata_path",
    "get_processed_data_path",
    "ensure_directories",
    "get_risk_level",
]
