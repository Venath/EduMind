"""
Tests for Prediction Module
============================
Tests for RiskPredictor class and inference.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))


class TestRiskPredictor:
    """Tests for RiskPredictor class."""
    
    def test_predictor_with_model(self, model_path, tmp_path):
        """Test predictor with trained model."""
        from src.models.predictor import RiskPredictor
        
        predictor = RiskPredictor(model_path=model_path)
        assert predictor.model is not None
    
    def test_predict_single(self, model_path, sample_features):
        """Test single prediction."""
        from src.models.predictor import RiskPredictor
        
        predictor = RiskPredictor(model_path=model_path)
        result = predictor.predict(sample_features)
        
        assert "prediction" in result
        assert "probability" in result
        assert "risk_level" in result
        assert result["prediction"]["class"] in [0, 1]
        assert 0 <= result["probability"]["at_risk"] <= 1
    
    def test_predict_batch(self, model_path, sample_dataframe):
        """Test batch prediction."""
        from src.models.predictor import RiskPredictor
        
        predictor = RiskPredictor(model_path=model_path)
        results = predictor.predict(sample_dataframe)
        
        assert len(results) == len(sample_dataframe)
        for result in results:
            assert "prediction" in result
            assert "risk_level" in result
    
    def test_predict_batch_dataframe(self, model_path, sample_dataframe):
        """Test batch prediction returning DataFrame."""
        from src.models.predictor import RiskPredictor
        
        predictor = RiskPredictor(model_path=model_path)
        result_df = predictor.predict_batch(sample_dataframe)
        
        assert isinstance(result_df, pd.DataFrame)
        assert "prediction_class" in result_df.columns
        assert "risk_level" in result_df.columns
        assert len(result_df) == len(sample_dataframe)
    
    def test_missing_features(self, model_path):
        """Test prediction with missing features."""
        from src.models.predictor import RiskPredictor
        
        predictor = RiskPredictor(model_path=model_path)
        
        incomplete_features = {
            "avg_grade": 65.0,
            # Missing other features
        }
        
        with pytest.raises(ValueError) as exc_info:
            predictor.predict(incomplete_features)
        
        assert "Missing required features" in str(exc_info.value)
    
    def test_feature_importance(self, model_path):
        """Test feature importance retrieval."""
        from src.models.predictor import RiskPredictor
        
        predictor = RiskPredictor(model_path=model_path)
        importance = predictor.get_feature_importance()
        
        assert isinstance(importance, dict)
        assert len(importance) > 0
    
    def test_model_info(self, model_path):
        """Test model info retrieval."""
        from src.models.predictor import RiskPredictor
        
        predictor = RiskPredictor(model_path=model_path)
        info = predictor.get_model_info()
        
        assert "feature_count" in info
        assert "feature_names" in info
        assert "classes" in info


class TestRiskLevels:
    """Tests for risk level classification."""
    
    def test_risk_level_thresholds(self, model_path, sample_features):
        """Test risk levels are correctly assigned."""
        from src.models.predictor import RiskPredictor
        from config.settings import RISK_THRESHOLDS
        
        predictor = RiskPredictor(model_path=model_path)
        result = predictor.predict(sample_features)
        
        risk_level = result["risk_level"]
        prob = result["probability"]["at_risk"]
        
        if prob < RISK_THRESHOLDS["low"]:
            assert risk_level == "low"
        elif prob < RISK_THRESHOLDS["medium"]:
            assert risk_level == "medium"
        elif prob < RISK_THRESHOLDS["high"]:
            assert risk_level == "high"
        else:
            assert risk_level == "critical"


class TestPredictionEdgeCases:
    """Tests for edge cases in prediction."""
    
    def test_extreme_values(self, model_path):
        """Test prediction with extreme feature values."""
        from src.models.predictor import RiskPredictor
        
        predictor = RiskPredictor(model_path=model_path)
        
        extreme_features = {
            "avg_grade": 0.0,
            "grade_consistency": 0.0,
            "grade_range": 100.0,
            "num_assessments": 0,
            "assessment_completion_rate": 0.0,
            "studied_credits": 0,
            "num_of_prev_attempts": 10,
            "low_performance": 1,
            "low_engagement": 1,
            "has_previous_attempts": 1,
        }
        
        result = predictor.predict(extreme_features)
        
        # Should predict high risk for poor performer
        assert result["probability"]["at_risk"] > 0.5
    
    def test_perfect_student(self, model_path):
        """Test prediction for high-performing student."""
        from src.models.predictor import RiskPredictor
        
        predictor = RiskPredictor(model_path=model_path)
        
        perfect_features = {
            "avg_grade": 95.0,
            "grade_consistency": 98.0,
            "grade_range": 5.0,
            "num_assessments": 10,
            "assessment_completion_rate": 1.0,
            "studied_credits": 120,
            "num_of_prev_attempts": 0,
            "low_performance": 0,
            "low_engagement": 0,
            "has_previous_attempts": 0,
        }
        
        result = predictor.predict(perfect_features)
        
        # Should predict low risk for good performer
        assert result["probability"]["at_risk"] < 0.5
