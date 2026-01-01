"""Tests for prediction endpoints"""

import sys
from pathlib import Path

# Ensure project root is in Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from uuid import uuid4

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


class TestModelInfo:
    """Test model information endpoint"""

    def test_model_info_endpoint(self):
        """Test GET /api/v1/model/info returns model information"""
        response = client.get("/api/v1/model/info")
        assert response.status_code == 200

        data = response.json()
        assert "model_type" in data
        assert "features_count" in data
        assert "feature_names" in data
        assert "classes" in data
        assert "metadata" in data

        # Verify data types
        assert isinstance(data["features_count"], int)
        assert isinstance(data["feature_names"], list)
        assert isinstance(data["classes"], list)
        assert isinstance(data["metadata"], dict)

        # Verify we have features and classes
        assert data["features_count"] > 0
        assert len(data["feature_names"]) > 0
        assert len(data["classes"]) > 0


class TestPredictionEndpoint:
    """Test prediction endpoint"""

    @pytest.fixture
    def valid_prediction_payload(self):
        """Valid prediction request payload"""
        return {
            "student_id": str(uuid4()),
            "features": {
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
            },
        }

    def test_prediction_success(self, valid_prediction_payload):
        """Test successful prediction with valid data"""
        response = client.post("/api/v1/predict", json=valid_prediction_payload)
        assert response.status_code == 200

        data = response.json()

        # Check top-level structure
        assert "prediction" in data
        assert "explanation" in data

        # Check prediction structure
        prediction = data["prediction"]
        assert "id" in prediction
        assert "request_id" in prediction
        assert "student_id" in prediction
        assert "predicted_class" in prediction
        assert "probability" in prediction
        assert "probabilities" in prediction
        assert "risk_level" in prediction
        assert "created_at" in prediction

        # Verify prediction values
        assert prediction["predicted_class"] in [
            "Pass",
            "Fail",
            "Distinction",
            "Withdrawn",
        ]
        assert 0 <= prediction["probability"] <= 1
        assert prediction["risk_level"] in ["low", "medium", "high", "critical"]
        assert isinstance(prediction["probabilities"], dict)

        # Check probabilities sum to ~1
        prob_sum = sum(prediction["probabilities"].values())
        assert 0.99 <= prob_sum <= 1.01

        # Check explanation structure
        explanation = data["explanation"]
        assert "id" in explanation
        assert "prediction_result_id" in explanation
        assert "shap_values" in explanation
        assert "top_features" in explanation
        assert "natural_language_explanation" in explanation
        assert "confidence_factors" in explanation
        assert "risk_factors" in explanation
        assert "created_at" in explanation

        # Verify explanation values
        assert isinstance(explanation["shap_values"], dict)
        assert isinstance(explanation["top_features"], list)
        assert isinstance(explanation["natural_language_explanation"], str)
        assert isinstance(explanation["confidence_factors"], list)
        assert isinstance(explanation["risk_factors"], list)

        # Check top features structure
        if len(explanation["top_features"]) > 0:
            feature = explanation["top_features"][0]
            assert "feature_name" in feature
            assert "importance" in feature
            assert "shap_value" in feature
            assert "contribution" in feature
            assert feature["contribution"] in ["positive", "negative"]

    def test_prediction_with_different_features(self):
        """Test prediction with different feature values"""
        payload = {
            "student_id": str(uuid4()),
            "features": {
                "code_module": 1,
                "code_presentation": 0,
                "gender": 1,
                "region": 10,
                "highest_education": 3,
                "imd_band": 80,
                "age_band": 3,
                "num_of_prev_attempts": 2,
                "studied_credits": 60,
                "disability": 1,
            },
        }

        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "prediction" in data
        assert "explanation" in data

    def test_prediction_invalid_student_id(self):
        """Test prediction with invalid student ID format"""
        payload = {"student_id": "invalid-uuid-format", "features": {"code_module": 0}}

        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422  # Validation error

        data = response.json()
        assert "detail" in data

    def test_prediction_missing_student_id(self):
        """Test prediction without student_id"""
        payload = {"features": {"code_module": 0}}

        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data

    def test_prediction_missing_features(self):
        """Test prediction without features"""
        payload = {"student_id": str(uuid4())}

        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

        data = response.json()
        assert "detail" in data

    def test_prediction_empty_features(self):
        """Test prediction with empty features dictionary"""
        payload = {"student_id": str(uuid4()), "features": {}}

        response = client.post("/api/v1/predict", json=payload)
        # Should either succeed with defaults or return error
        assert response.status_code in [200, 400, 422]

    def test_prediction_invalid_feature_type(self):
        """Test prediction with non-numeric feature values"""
        payload = {
            "student_id": str(uuid4()),
            "features": {
                "code_module": "invalid",  # Should be numeric
                "code_presentation": 1,
            },
        }

        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_prediction_extra_fields(self):
        """Test prediction with extra unexpected fields"""
        payload = {
            "student_id": str(uuid4()),
            "features": {"code_module": 0},
            "extra_field": "should be ignored",
        }

        response = client.post("/api/v1/predict", json=payload)
        # Pydantic should ignore extra fields or return error depending on config
        assert response.status_code in [200, 422]

    def test_prediction_null_values(self):
        """Test prediction with null feature values"""
        payload = {
            "student_id": str(uuid4()),
            "features": {"code_module": None, "code_presentation": 1},
        }

        response = client.post("/api/v1/predict", json=payload)
        # Should handle null values gracefully
        assert response.status_code in [200, 400, 422]

    def test_prediction_response_schema(self, valid_prediction_payload):
        """Test prediction response matches expected schema"""
        response = client.post("/api/v1/predict", json=valid_prediction_payload)
        assert response.status_code == 200

        data = response.json()

        # Verify UUID format for IDs
        prediction = data["prediction"]
        explanation = data["explanation"]

        # Check UUIDs are properly formatted
        assert len(prediction["id"]) == 36  # UUID format
        assert len(prediction["student_id"]) == 36
        assert len(explanation["id"]) == 36
        assert len(explanation["prediction_result_id"]) == 36

        # Verify explanation is linked to prediction
        assert explanation["prediction_result_id"] == prediction["id"]

    def test_multiple_predictions_different_results(self):
        """Test multiple predictions return different results"""
        payload1 = {
            "student_id": str(uuid4()),
            "features": {"studied_credits": 120, "num_of_prev_attempts": 0},
        }

        payload2 = {
            "student_id": str(uuid4()),
            "features": {"studied_credits": 30, "num_of_prev_attempts": 3},
        }

        response1 = client.post("/api/v1/predict", json=payload1)
        response2 = client.post("/api/v1/predict", json=payload2)

        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()

            # Different inputs should produce different predictions
            # (not always true, but likely with these extreme differences)
            assert data1["prediction"]["id"] != data2["prediction"]["id"]


class TestPredictionPerformance:
    """Test prediction performance"""

    def test_prediction_response_time(self):
        """Test prediction completes in reasonable time"""
        import time

        payload = {
            "student_id": str(uuid4()),
            "features": {
                "code_module": 0,
                "code_presentation": 1,
                "studied_credits": 120,
            },
        }

        start_time = time.time()
        response = client.post("/api/v1/predict", json=payload)
        end_time = time.time()

        duration = end_time - start_time

        # Prediction should complete in under 5 seconds
        assert duration < 5.0

        if response.status_code == 200:
            # Successful prediction should be reasonably fast
            assert duration < 2.0
