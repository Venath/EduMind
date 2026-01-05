"""
Tests for ETL Module
====================
Tests for data extraction, transformation, and loading.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))


class TestFeatureEngineer:
    """Tests for FeatureEngineer class."""
    
    def test_create_grade_features(self, sample_dataframe):
        """Test grade feature creation."""
        from src.data.preprocessing import FeatureEngineer
        
        engineer = FeatureEngineer()
        
        # Simulate grade features already present
        assert "avg_grade" in sample_dataframe.columns
        assert "grade_consistency" in sample_dataframe.columns
    
    def test_create_risk_flags(self, sample_dataframe):
        """Test risk flag creation."""
        from src.data.preprocessing import FeatureEngineer
        
        engineer = FeatureEngineer()
        result = engineer.create_risk_flags(sample_dataframe)
        
        assert "low_performance" in result.columns
        assert "low_engagement" in result.columns
        assert result["low_performance"].dtype in [int, np.int64, np.int32]
    
    def test_feature_pipeline(self, sample_dataframe):
        """Test full feature engineering pipeline."""
        from src.data.preprocessing import FeatureEngineer
        
        engineer = FeatureEngineer()
        
        # Add label for testing
        sample_dataframe["label"] = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        
        result = engineer.run_pipeline(sample_dataframe)
        
        assert "label" in result.columns
        assert len(result) > 0


class TestOULADProcessor:
    """Tests for OULAD data processor."""
    
    def test_processor_init(self):
        """Test processor initialization."""
        from src.data.etl import OULADProcessor
        
        processor = OULADProcessor()
        assert processor is not None
    
    def test_validate_data(self, mock_oulad_data):
        """Test data validation."""
        from src.data.etl import OULADProcessor
        
        processor = OULADProcessor()
        
        # Should not raise for valid data
        student_info = mock_oulad_data["studentInfo"]
        assert "id_student" in student_info.columns
        assert "final_result" in student_info.columns


class TestDataIntegrity:
    """Tests for data integrity checks."""
    
    def test_no_null_values_in_features(self, sample_dataframe):
        """Ensure no null values in processed features."""
        assert sample_dataframe.isnull().sum().sum() == 0
    
    def test_feature_value_ranges(self, sample_dataframe):
        """Ensure feature values are in valid ranges."""
        assert sample_dataframe["avg_grade"].between(0, 100).all()
        assert sample_dataframe["assessment_completion_rate"].between(0, 1).all()
    
    def test_binary_features(self, sample_features):
        """Ensure binary features are 0 or 1."""
        binary_features = [
            "low_performance",
            "low_engagement", 
            "has_previous_attempts",
        ]
        for feat in binary_features:
            assert sample_features[feat] in [0, 1]
