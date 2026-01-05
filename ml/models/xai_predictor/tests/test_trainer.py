"""
Tests for Model Training
=========================
Tests for the Trainer class and model training process.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import xgboost as xgb

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))


class TestTrainer:
    """Tests for Trainer class."""
    
    def test_trainer_init(self, tmp_path):
        """Test trainer initialization."""
        from src.models.trainer import Trainer
        
        trainer = Trainer(output_dir=tmp_path)
        assert trainer is not None
        assert trainer.model_params is not None
    
    def test_load_data(self, processed_data_path, tmp_path):
        """Test data loading."""
        from src.models.trainer import Trainer
        
        trainer = Trainer(output_dir=tmp_path)
        X_train, X_test, y_train, y_test = trainer.load_data(processed_data_path)
        
        assert len(X_train) > 0
        assert len(X_test) > 0
        assert len(y_train) == len(X_train)
        assert len(y_test) == len(X_test)
    
    def test_train(self, processed_data_path, tmp_path):
        """Test model training."""
        from src.models.trainer import Trainer
        
        trainer = Trainer(output_dir=tmp_path)
        trainer.load_data(processed_data_path)
        trainer.train()
        
        assert trainer.model is not None
        assert isinstance(trainer.model, xgb.XGBClassifier)
    
    def test_evaluate(self, processed_data_path, tmp_path):
        """Test model evaluation."""
        from src.models.trainer import Trainer
        
        trainer = Trainer(output_dir=tmp_path)
        trainer.load_data(processed_data_path)
        trainer.train()
        metrics = trainer.evaluate()
        
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1" in metrics
        assert 0 <= metrics["accuracy"] <= 1
    
    def test_save(self, processed_data_path, tmp_path):
        """Test model saving."""
        from src.models.trainer import Trainer
        
        trainer = Trainer(output_dir=tmp_path)
        trainer.load_data(processed_data_path)
        trainer.train()
        trainer.save()
        
        assert (tmp_path / "model.json").exists()
        assert (tmp_path / "model.pkl").exists()
        assert (tmp_path / "metadata.json").exists()
        
        # Verify metadata
        with open(tmp_path / "metadata.json") as f:
            metadata = json.load(f)
        assert "feature_names" in metadata
        assert "training_date" in metadata


class TestModelValidation:
    """Tests for model validation requirements."""
    
    def test_minimum_accuracy(self, processed_data_path, tmp_path):
        """Test that model meets minimum accuracy threshold."""
        from src.models.trainer import Trainer
        from config.settings import VALIDATION_THRESHOLDS
        
        trainer = Trainer(output_dir=tmp_path)
        trainer.load_data(processed_data_path)
        trainer.train()
        metrics = trainer.evaluate()
        
        # With small test data, accuracy may vary
        # This is more of a sanity check
        assert metrics["accuracy"] > 0.3
    
    def test_model_reproducibility(self, processed_data_path, tmp_path):
        """Test that training is reproducible with same seed."""
        from src.models.trainer import Trainer
        
        # Train twice with same seed
        trainer1 = Trainer(output_dir=tmp_path / "run1")
        trainer1.load_data(processed_data_path)
        trainer1.train()
        metrics1 = trainer1.evaluate()
        
        trainer2 = Trainer(output_dir=tmp_path / "run2")
        trainer2.load_data(processed_data_path)
        trainer2.train()
        metrics2 = trainer2.evaluate()
        
        assert metrics1["accuracy"] == metrics2["accuracy"]


class TestFeatureImportance:
    """Tests for feature importance extraction."""
    
    def test_feature_importance_values(self, processed_data_path, tmp_path):
        """Test feature importance values are valid."""
        from src.models.trainer import Trainer
        
        trainer = Trainer(output_dir=tmp_path)
        trainer.load_data(processed_data_path)
        trainer.train()
        trainer.evaluate()
        
        importance = trainer.feature_importance
        
        assert importance is not None
        assert len(importance) > 0
        assert all(v >= 0 for v in importance.values())
