import json
import logging
from pathlib import Path
from typing import List, Tuple

import numpy as np
import xgboost as xgb
from app.schemas.academic_risk import AcademicRiskRequest, AcademicRiskResponse

logger = logging.getLogger(__name__)


class AcademicRiskService:
    """Service for academic risk prediction using OULAD model"""

    def __init__(self):
        self.model = None
        self.metadata = None
        self.feature_names = None
        self._load_model()

    def _load_model(self):
        """Load the trained OULAD academic risk model"""
        try:
            # Path to saved models
            base_path = Path(__file__).parent.parent.parent / "saved_models"

            logger.info(f"Loading OULAD model from: {base_path}")

            if not base_path.exists():
                logger.warning(f"Model directory not found: {base_path}")
                logger.info("Academic risk service will run in demo mode")
                self._setup_demo_mode()
                return

            # Load XGBoost model
            model_path = base_path / "academic_risk_model.json"
            if not model_path.exists():
                logger.warning(f"Model file not found: {model_path}")
                self._setup_demo_mode()
                return

            self.model = xgb.XGBClassifier()
            self.model.load_model(str(model_path))
            logger.info("✓ OULAD model loaded successfully")

            # Load metadata
            metadata_path = base_path / "model_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    self.metadata = json.load(f)
                self.feature_names = self.metadata.get(
                    "feature_names", self._get_default_features()
                )
                accuracy = self.metadata.get("accuracy", 0)
                logger.info(f"✓ Loaded {len(self.feature_names)} features")
                logger.info(f"✓ Model accuracy: {accuracy*100:.1f}%")
            else:
                self.feature_names = self._get_default_features()
                self.metadata = {
                    "model_type": "XGBoost",
                    "feature_names": self.feature_names,
                }

        except Exception as e:
            logger.error(f"Error loading OULAD model: {str(e)}")
            logger.info("Falling back to demo mode")
            self._setup_demo_mode()

    def _get_default_features(self) -> List[str]:
        """Get default feature names"""
        return [
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

    def _setup_demo_mode(self):
        """Setup demo mode without a real model"""
        self.model = None
        self.feature_names = self._get_default_features()
        self.metadata = {
            "model_type": "Demo Mode",
            "description": "Running without trained model - simulated predictions",
            "feature_names": self.feature_names,
        }
        logger.info("Running academic risk service in demo mode")

    def _prepare_features(self, request: AcademicRiskRequest) -> np.ndarray:
        """Prepare features in correct order for model"""
        features = np.array(
            [
                [
                    request.avg_grade,
                    request.grade_consistency,
                    request.grade_range,
                    request.num_assessments,
                    request.assessment_completion_rate,
                    request.studied_credits,
                    request.num_of_prev_attempts,
                    request.low_performance,
                    request.low_engagement,
                    request.has_previous_attempts,
                ]
            ]
        )
        return features

    def _generate_recommendations(
        self, request: AcademicRiskRequest, prediction: int
    ) -> List[str]:
        """Generate personalized recommendations based on risk level"""
        recommendations = []

        if prediction == 1:  # At-Risk
            if request.avg_grade < 50:
                recommendations.append(
                    f"Seek immediate tutoring - current grade ({request.avg_grade:.1f}%) is critically low"
                )
            elif request.avg_grade < 60:
                recommendations.append(
                    f"Improve study strategies - grade ({request.avg_grade:.1f}%) is below average"
                )

            if request.num_assessments < 5:
                recommendations.append(
                    f"Complete all remaining assessments - only {request.num_assessments} completed"
                )

            if request.has_previous_attempts == 1:
                recommendations.append(
                    "Address knowledge gaps from previous course attempts"
                )

            if request.low_performance == 1:
                recommendations.append("Consider reducing course load if overwhelmed")

            recommendations.append("Contact academic advisor immediately")
            recommendations.append("Join study groups or tutoring sessions")

        else:  # Safe
            recommendations.append(
                f"Maintain current performance (grade: {request.avg_grade:.1f}%)"
            )
            recommendations.append("Help struggling peers through peer mentoring")

            if request.avg_grade < 80:
                recommendations.append("Aim for distinction level (80%+)")

            recommendations.append("Explore advanced learning materials")
            recommendations.append("Maintain consistent study habits")

        return recommendations

    def _get_top_risk_factors(
        self, request: AcademicRiskRequest, prediction: int
    ) -> List[dict]:
        """Identify top risk factors"""
        factors = []

        if prediction == 1:  # At-Risk
            if request.avg_grade < 50:
                factors.append(
                    {
                        "feature": "avg_grade",
                        "value": request.avg_grade,
                        "impact": "critical",
                    }
                )
            elif request.avg_grade < 60:
                factors.append(
                    {
                        "feature": "avg_grade",
                        "value": request.avg_grade,
                        "impact": "high",
                    }
                )

            if request.num_assessments < 5:
                factors.append(
                    {
                        "feature": "num_assessments",
                        "value": request.num_assessments,
                        "impact": "high",
                    }
                )

            if request.has_previous_attempts == 1:
                factors.append(
                    {
                        "feature": "previous_attempts",
                        "value": request.num_of_prev_attempts,
                        "impact": "high",
                    }
                )

            if request.low_engagement == 1:
                factors.append(
                    {"feature": "low_engagement", "value": 1, "impact": "medium"}
                )

        return factors[:5]  # Top 5 factors

    async def predict(self, request: AcademicRiskRequest) -> AcademicRiskResponse:
        """Make academic risk prediction"""
        try:
            # Prepare features
            features = self._prepare_features(request)

            if self.model is not None:
                # Real model prediction
                prediction = self.model.predict(features)[0]
                probabilities = self.model.predict_proba(features)[0]
            else:
                # Demo mode prediction
                prediction, probabilities = self._demo_predict(request)

            risk_level = "At-Risk" if prediction == 1 else "Safe"
            risk_score = float(probabilities[1])  # Probability of being at-risk
            confidence = float(probabilities[prediction])

            # Generate recommendations
            recommendations = self._generate_recommendations(request, prediction)

            # Get top risk factors
            top_risk_factors = self._get_top_risk_factors(request, prediction)

            # Create response
            response = AcademicRiskResponse(
                student_id=request.student_id,
                risk_level=risk_level,
                risk_score=risk_score,
                confidence=confidence,
                probabilities={
                    "Safe": float(probabilities[0]),
                    "At-Risk": float(probabilities[1]),
                },
                recommendations=recommendations,
                top_risk_factors=top_risk_factors,
            )

            logger.info(
                f"Prediction for {request.student_id}: {risk_level} (confidence: {confidence:.2%})"
            )

            return response

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise

    def _demo_predict(self, request: AcademicRiskRequest) -> Tuple[int, np.ndarray]:
        """Generate simulated prediction for demo mode"""
        # Simple heuristic-based prediction
        risk_score = 0.3

        if request.avg_grade < 40:
            risk_score += 0.3
        elif request.avg_grade < 60:
            risk_score += 0.15

        if request.num_assessments < 5:
            risk_score += 0.1

        if request.has_previous_attempts == 1:
            risk_score += 0.15

        if request.low_engagement == 1:
            risk_score += 0.1

        if request.low_performance == 1:
            risk_score += 0.1

        risk_score = min(max(risk_score, 0.0), 1.0)
        prediction = 1 if risk_score > 0.5 else 0
        probabilities = np.array([1 - risk_score, risk_score])

        return prediction, probabilities


# Initialize service (singleton)
academic_risk_service = AcademicRiskService()
