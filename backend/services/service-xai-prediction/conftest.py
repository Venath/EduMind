"""Pytest configuration and fixtures"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment and mock ML models if needed"""
    try:
        from app.Services.ml_service import ml_service

        # Check if models are loaded
        if ml_service.model is None:
            # Mock the ML service if models aren't available
            mock_model = MagicMock()
            mock_model.predict_proba.return_value = np.array([[0.1, 0.7, 0.15, 0.05]])

            mock_scaler = MagicMock()
            mock_scaler.transform.return_value = np.array([[0.5] * 33])

            mock_encoder = MagicMock()
            mock_encoder.inverse_transform.return_value = np.array(["Pass"])
            mock_encoder.classes_ = np.array(
                ["Pass", "Fail", "Distinction", "Withdrawn"]
            )

            mock_explainer = MagicMock()
            mock_explainer.shap_values.return_value = np.array([[0.1] * 33])

            # Set mocked attributes
            ml_service.model = mock_model
            ml_service.scaler = mock_scaler
            ml_service.label_encoder = mock_encoder
            ml_service.feature_names = [f"feature_{i}" for i in range(33)]
            ml_service.metadata = {"model_version": "test", "accuracy": 0.88}
            ml_service.explainer = mock_explainer

            print("ML models not found - using mocked models for testing")
        else:
            print("ML models loaded successfully")

    except Exception as e:
        print(f"Error setting up test environment: {e}")
        # Continue with tests anyway

    yield

    # Cleanup
    pass


@pytest.fixture
def sample_student_features():
    """Sample student features for testing"""
    return {
        "code_module": 0,
        "code_presentation": 1,
        "gender": 0,
        "region": 5,
        "highest_education": 2,
        "imd_band": 50,
        "age_band": 2,
        "num_of_prev_attempts": 0,
        "studied_credits": 120,
        "disability": 0,
    }


@pytest.fixture
def sample_student_id():
    """Sample student ID for testing"""
    from uuid import uuid4

    return str(uuid4())
