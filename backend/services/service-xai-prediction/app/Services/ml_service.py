"""
ML Service for XAI Prediction
A lightweight service that handles predictions and explanations
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
from app.core.config import settings
from app.schemas.prediction import (
    ExplanationResult,
    FeatureContribution,
    PredictionRequest,
    PredictionResult,
)

logger = logging.getLogger(__name__)


class MLService:
    """Machine Learning Service for student outcome prediction"""

    def __init__(self):
        self.model = None
        self.explainer = None
        self.label_encoder = None
        self.feature_names: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self._load_model()

    def _load_model(self):
        """Load the trained model and supporting files"""
        try:
            base_path = Path(__file__).parent.parent.parent / "saved_models"

            if not base_path.exists():
                logger.warning(f"Model directory not found: {base_path}")
                logger.info("Service will run in demo mode without a trained model")
                self._setup_demo_mode()
                return

            # Try to load model
            model_path = base_path / "xai_model.joblib"
            if model_path.exists():
                self.model = joblib.load(model_path)
                logger.info("✓ Model loaded successfully")
            else:
                # Try alternative path
                model_path = base_path / "academic_risk_model.json"
                if model_path.exists():
                    import xgboost as xgb

                    self.model = xgb.XGBClassifier()
                    self.model.load_model(str(model_path))
                    logger.info("✓ XGBoost model loaded successfully")
                else:
                    logger.warning("No model file found, running in demo mode")
                    self._setup_demo_mode()
                    return

            # Load metadata if exists
            metadata_path = base_path / "model_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    self.metadata = json.load(f)
                self.feature_names = self.metadata.get("feature_names", [])
                logger.info(
                    f"✓ Loaded metadata with {len(self.feature_names)} features"
                )

            # Load label encoder if exists
            encoder_path = base_path / "label_encoder.joblib"
            if encoder_path.exists():
                self.label_encoder = joblib.load(encoder_path)
                logger.info("✓ Label encoder loaded")
            else:
                # Create a simple mock encoder
                self._setup_mock_encoder()

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.info("Setting up demo mode")
            self._setup_demo_mode()

    def _setup_demo_mode(self):
        """Setup demo mode without a real model"""
        self.feature_names = [
            "total_interactions",
            "avg_response_time",
            "consistency_score",
            "days_inactive",
            "completion_rate",
            "assessment_score",
        ]
        self.metadata = {
            "model_type": "Demo Mode",
            "description": "No trained model loaded - returning simulated predictions",
            "feature_names": self.feature_names,
        }
        self._setup_mock_encoder()
        logger.info("Running in demo mode")

    def _setup_mock_encoder(self):
        """Create a mock label encoder"""

        class MockEncoder:
            classes_ = np.array(["safe", "at_risk"])

            def transform(self, x):
                return [0 if v == "safe" else 1 for v in x]

            def inverse_transform(self, x):
                return ["safe" if v == 0 else "at_risk" for v in x]

        self.label_encoder = MockEncoder()

    def _prepare_features(self, request: PredictionRequest) -> np.ndarray:
        """Convert request to feature array"""
        features = np.array(
            [
                request.total_interactions,
                request.avg_response_time,
                request.consistency_score,
                request.days_inactive,
                request.completion_rate,
                request.assessment_score,
            ]
        ).reshape(1, -1)
        return features

    def _get_risk_level(self, probability: float) -> str:
        """Determine risk level from probability"""
        if probability < 0.3:
            return "low"
        elif probability < 0.7:
            return "medium"
        else:
            return "high"

    def _generate_explanation(
        self, request: PredictionRequest, prediction_prob: float
    ) -> ExplanationResult:
        """Generate XAI explanation for prediction"""
        # Feature contributions (simulated for demo)
        contributions = []

        # Days inactive contribution
        if request.days_inactive > 7:
            contributions.append(
                FeatureContribution(
                    feature="days_inactive",
                    value=request.days_inactive,
                    contribution=0.15 * (request.days_inactive / 30),
                    impact="negative",
                )
            )

        # Total interactions contribution
        if request.total_interactions < 100:
            contributions.append(
                FeatureContribution(
                    feature="total_interactions",
                    value=request.total_interactions,
                    contribution=-0.1 * (1 - request.total_interactions / 200),
                    impact="negative",
                )
            )
        else:
            contributions.append(
                FeatureContribution(
                    feature="total_interactions",
                    value=request.total_interactions,
                    contribution=0.1,
                    impact="positive",
                )
            )

        # Consistency score contribution
        contributions.append(
            FeatureContribution(
                feature="consistency_score",
                value=request.consistency_score,
                contribution=0.2 * (request.consistency_score - 0.5),
                impact="positive" if request.consistency_score > 0.5 else "negative",
            )
        )

        # Sort by absolute contribution
        contributions.sort(key=lambda x: abs(x.contribution), reverse=True)

        top_positive = [c.feature for c in contributions if c.impact == "positive"][:3]
        top_negative = [c.feature for c in contributions if c.impact == "negative"][:3]

        return ExplanationResult(
            feature_contributions=contributions,
            top_positive_factors=top_positive,
            top_negative_factors=top_negative,
            shap_values=None,
            base_value=0.5,
        )

    def _generate_recommendations(
        self, request: PredictionRequest, risk_level: str
    ) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []

        if request.days_inactive > 7:
            recommendations.append("Resume learning activities to stay on track")

        if request.total_interactions < 100:
            recommendations.append("Increase engagement with course materials")

        if request.completion_rate < 0.5:
            recommendations.append("Complete pending modules and assignments")

        if request.consistency_score < 0.5:
            recommendations.append("Establish a regular study schedule")

        if request.assessment_score < 60:
            recommendations.append(
                "Review materials and practice with additional exercises"
            )

        if risk_level == "high":
            recommendations.insert(
                0, "[WARNING] Consider scheduling a meeting with your academic advisor"
            )

        return recommendations[:5]  # Return top 5 recommendations

    async def predict(
        self, request: PredictionRequest
    ) -> Tuple[PredictionResult, ExplanationResult]:
        """
        Make prediction with XAI explanation

        Returns:
            Tuple of (PredictionResult, ExplanationResult)
        """
        # Prepare features
        features = self._prepare_features(request)

        if self.model is not None:
            # Real model prediction
            try:
                prediction_proba = self.model.predict_proba(features)[0]
                at_risk_prob = (
                    float(prediction_proba[1])
                    if len(prediction_proba) > 1
                    else float(prediction_proba[0])
                )
                predicted_class = "at_risk" if at_risk_prob > 0.5 else "safe"
            except Exception as e:
                logger.error(f"Prediction error: {e}")
                # Fallback to demo prediction
                at_risk_prob = self._demo_prediction(request)
                predicted_class = "at_risk" if at_risk_prob > 0.5 else "safe"
        else:
            # Demo mode prediction
            at_risk_prob = self._demo_prediction(request)
            predicted_class = "at_risk" if at_risk_prob > 0.5 else "safe"

        risk_level = self._get_risk_level(at_risk_prob)

        prediction = PredictionResult(
            predicted_class=predicted_class,
            probability=at_risk_prob,
            risk_level=risk_level,
        )

        explanation = self._generate_explanation(request, at_risk_prob)

        return prediction, explanation

    def _demo_prediction(self, request: PredictionRequest) -> float:
        """Generate a simulated prediction for demo mode"""
        # Simple heuristic-based prediction
        risk_score = 0.5

        # Days inactive increases risk
        risk_score += min(request.days_inactive / 30, 0.2)

        # Low interactions increase risk
        if request.total_interactions < 100:
            risk_score += 0.1
        elif request.total_interactions > 200:
            risk_score -= 0.1

        # Low consistency increases risk
        risk_score -= (request.consistency_score - 0.5) * 0.2

        # Low completion rate increases risk
        risk_score -= (request.completion_rate - 0.5) * 0.15

        # Low scores increase risk
        risk_score -= (request.assessment_score - 50) / 100 * 0.15

        return max(0.0, min(1.0, risk_score))


# Singleton instance
ml_service = MLService()
