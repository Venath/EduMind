"""
Pytest Fixtures for XAI Predictor Tests
=======================================
Shared fixtures used across test modules.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_features() -> dict:
    """Sample feature dictionary for testing."""
    return {
        "avg_grade": 65.0,
        "grade_consistency": 85.0,
        "grade_range": 20.0,
        "num_assessments": 5,
        "assessment_completion_rate": 0.75,
        "studied_credits": 60,
        "num_of_prev_attempts": 0,
        "low_performance": 0,
        "low_engagement": 0,
        "has_previous_attempts": 0,
    }


@pytest.fixture
def sample_dataframe(sample_features) -> pd.DataFrame:
    """Sample DataFrame with multiple rows for testing."""
    data = []
    for i in range(10):
        row = sample_features.copy()
        row["avg_grade"] = 40 + i * 5  # Vary grades
        row["assessment_completion_rate"] = 0.5 + i * 0.05
        data.append(row)
    return pd.DataFrame(data)


@pytest.fixture
def mock_oulad_data() -> dict:
    """Mock OULAD data for ETL testing."""
    n_students = 100
    
    return {
        "studentInfo": pd.DataFrame({
            "id_student": range(n_students),
            "code_module": ["AAA"] * n_students,
            "code_presentation": ["2014J"] * n_students,
            "studied_credits": np.random.choice([60, 120], n_students),
            "num_of_prev_attempts": np.random.randint(0, 3, n_students),
            "final_result": np.random.choice(["Pass", "Fail", "Withdrawn"], n_students),
        }),
        "studentAssessment": pd.DataFrame({
            "id_student": np.repeat(range(n_students), 5),
            "id_assessment": np.tile(range(5), n_students),
            "score": np.random.randint(0, 100, n_students * 5),
            "is_banked": [0] * (n_students * 5),
        }),
        "assessments": pd.DataFrame({
            "id_assessment": range(5),
            "code_module": ["AAA"] * 5,
            "code_presentation": ["2014J"] * 5,
            "assessment_type": ["TMA"] * 5,
            "weight": [20.0] * 5,
        }),
    }


@pytest.fixture
def processed_data_path(tmp_path) -> Path:
    """Create temporary processed data for testing."""
    data = pd.DataFrame({
        "avg_grade": [75, 45, 82, 33, 68, 55, 90, 42, 78, 50],
        "grade_consistency": [90, 60, 95, 40, 85, 70, 98, 55, 88, 65],
        "grade_range": [15, 45, 10, 60, 20, 35, 5, 50, 12, 40],
        "num_assessments": [5, 3, 5, 2, 4, 3, 5, 2, 5, 3],
        "assessment_completion_rate": [1.0, 0.6, 1.0, 0.4, 0.8, 0.6, 1.0, 0.4, 1.0, 0.6],
        "studied_credits": [60, 60, 120, 60, 60, 120, 60, 60, 120, 60],
        "num_of_prev_attempts": [0, 1, 0, 2, 0, 1, 0, 2, 0, 1],
        "low_performance": [0, 1, 0, 1, 0, 0, 0, 1, 0, 1],
        "low_engagement": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        "has_previous_attempts": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        "label": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    })
    
    path = tmp_path / "processed_data.csv"
    data.to_csv(path, index=False)
    return path


@pytest.fixture
def model_path(tmp_path, processed_data_path) -> Path:
    """Create a trained model for testing."""
    import xgboost as xgb
    
    data = pd.read_csv(processed_data_path)
    X = data.drop("label", axis=1)
    y = data["label"]
    
    model = xgb.XGBClassifier(
        n_estimators=10,
        max_depth=3,
        random_state=42,
    )
    model.fit(X, y)
    
    model_file = tmp_path / "model.json"
    model.save_model(str(model_file))
    
    return model_file
