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

            # Load XGBoost model using Booster API
            model_path = base_path / "academic_risk_model.json"
            if not model_path.exists():
                logger.warning(f"Model file not found: {model_path}")
                self._setup_demo_mode()
                return

            # Load as Booster (raw model)
            self.model = xgb.Booster()
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

    def _prepare_features(self, request: AcademicRiskRequest) -> xgb.DMatrix:
        """Prepare features as DMatrix for XGBoost Booster"""
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
        # Create DMatrix with feature names
        return xgb.DMatrix(features, feature_names=self.feature_names)

    def _generate_recommendations(
        self, request: AcademicRiskRequest, prediction: int, risk_score: float
    ) -> List[str]:
        """Generate personalized recommendations based on risk level"""
        recommendations = []

        if prediction == 2:  # At-Risk
            # Critical interventions
            recommendations.append(
                f"[URGENT] Grade {request.avg_grade:.1f}% requires immediate action"
            )
            recommendations.append(
                "Schedule emergency meeting with academic advisor TODAY"
            )
            recommendations.append(
                "Contact student support services immediately"
            )
            recommendations.append(
                "Attend ALL remaining classes and support sessions"
            )
            recommendations.append(
                "Dedicate minimum 15-20 hours/week to this course"
            )
            recommendations.append(
                "Get a study buddy or peer mentor assigned"
            )
            recommendations.append(
                "Focus on completing ALL remaining assessments"
            )
            recommendations.append(
                "Consider academic skills workshops (time management, study techniques)"
            )

        elif prediction == 1:  # Medium Risk
            recommendations.append(
                f"[WARNING] Current grade {request.avg_grade:.1f}% - aim to improve to 70%+"
            )
            recommendations.append(
                "Schedule regular check-ins with your tutor (weekly)"
            )
            recommendations.append(
                "Join study groups for collaborative learning"
            )
            recommendations.append(
                "Create a structured study schedule and stick to it"
            )
            recommendations.append(
                "Focus on completing all remaining assessments"
            )
            recommendations.append(
                "Review and revise topics where you scored lowest"
            )
            recommendations.append(
                "Attend all available support sessions and office hours"
            )

        else:  # Safe (prediction == 0)
            recommendations.append(
                f"[SUCCESS] Excellent work! Maintain current performance (grade: {request.avg_grade:.1f}%)"
            )
            recommendations.append(
                "Continue completing all assessments on time"
            )
            recommendations.append(
                "Work on maintaining consistency across assessments"
            )
            recommendations.append(
                "Consider helping peers through peer mentoring"
            )
            recommendations.append(
                "Explore advanced learning materials and challenges"
            )
            recommendations.append(
                "Aim for distinction level (80%+) performance"
            )

        return recommendations

    def _get_top_risk_factors(
        self, request: AcademicRiskRequest, prediction: int
    ) -> List[dict]:
        """Identify top risk factors for all risk levels"""
        factors = []

        if prediction == 1:  # At-Risk
            # Critical and high-impact factors
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
                    {"feature": "low_engagement", "value": 1, "impact": "high"}
                )

            if request.grade_consistency < 70:
                factors.append(
                    {
                        "feature": "grade_consistency",
                        "value": request.grade_consistency,
                        "impact": "medium",
                    }
                )

            if request.assessment_completion_rate < 0.7:
                factors.append(
                    {
                        "feature": "assessment_completion_rate",
                        "value": request.assessment_completion_rate,
                        "impact": "medium",
                    }
                )

        elif prediction == 0:  # Medium Risk
            # Monitor these areas for potential improvement
            if 60 <= request.avg_grade < 70:
                factors.append(
                    {
                        "feature": "avg_grade",
                        "value": request.avg_grade,
                        "impact": "medium",
                    }
                )

            if request.grade_consistency < 80:
                factors.append(
                    {
                        "feature": "grade_consistency",
                        "value": request.grade_consistency,
                        "impact": "medium",
                    }
                )

            if request.num_assessments < 8:
                factors.append(
                    {
                        "feature": "num_assessments",
                        "value": request.num_assessments,
                        "impact": "medium",
                    }
                )

            if request.assessment_completion_rate < 0.8:
                factors.append(
                    {
                        "feature": "assessment_completion_rate",
                        "value": request.assessment_completion_rate,
                        "impact": "medium",
                    }
                )

            if request.low_engagement == 1:
                factors.append(
                    {"feature": "low_engagement", "value": 1, "impact": "medium"}
                )

            if request.has_previous_attempts == 1:
                factors.append(
                    {
                        "feature": "previous_attempts",
                        "value": request.num_of_prev_attempts,
                        "impact": "low",
                    }
                )

        else:  # Safe (prediction == 2)
            # Highlight strengths and areas to maintain
            if request.avg_grade >= 70:
                factors.append(
                    {
                        "feature": "avg_grade",
                        "value": request.avg_grade,
                        "impact": "strength",
                    }
                )

            if request.grade_consistency >= 85:
                factors.append(
                    {
                        "feature": "grade_consistency",
                        "value": request.grade_consistency,
                        "impact": "strength",
                    }
                )

            if request.assessment_completion_rate >= 0.85:
                factors.append(
                    {
                        "feature": "assessment_completion_rate",
                        "value": request.assessment_completion_rate,
                        "impact": "strength",
                    }
                )

            if request.num_assessments >= 8:
                factors.append(
                    {
                        "feature": "num_assessments",
                        "value": request.num_assessments,
                        "impact": "strength",
                    }
                )

            if request.low_engagement == 0:
                factors.append(
                    {"feature": "engagement_level", "value": "High", "impact": "strength"}
                )

            # If no major strengths identified, add baseline factors
            if len(factors) == 0:
                factors.append(
                    {
                        "feature": "avg_grade",
                        "value": request.avg_grade,
                        "impact": "neutral",
                    }
                )
                factors.append(
                    {
                        "feature": "assessment_completion_rate",
                        "value": request.assessment_completion_rate,
                        "impact": "neutral",
                    }
                )

        return factors[:5]  # Top 5 factors

    async def predict(self, request: AcademicRiskRequest) -> AcademicRiskResponse:
        """Make academic risk prediction"""
        try:
            if self.model is not None:
                # Real model prediction using Booster API
                dmatrix = self._prepare_features(request)
                raw_predictions = self.model.predict(dmatrix)
                
                # Check if multi-class (3 probabilities) or binary (1 probability)
                if len(raw_predictions[0]) == 3:
                    # Multi-class: [prob_safe, prob_medium, prob_at_risk]
                    prob_safe = float(raw_predictions[0][0])
                    prob_medium = float(raw_predictions[0][1])
                    prob_at_risk = float(raw_predictions[0][2])
                    
                    # Determine prediction based on highest probability
                    prediction = int(np.argmax([prob_safe, prob_medium, prob_at_risk]))
                    
                    # Log the prediction
                    logger.info(f"Model prediction (multi-class) - Student: {request.student_id}, "
                               f"Prob Safe: {prob_safe:.4f}, Prob Medium: {prob_medium:.4f}, "
                               f"Prob At-Risk: {prob_at_risk:.4f}, Predicted: {prediction}")
                    
                    probabilities = np.array([prob_safe, prob_medium, prob_at_risk])
                else:
                    # Binary: single probability for at-risk class
                    prob_at_risk = float(raw_predictions[0])
                    prob_at_risk = max(0.0, min(1.0, prob_at_risk))
                    prob_safe = 1.0 - prob_at_risk
                    
                    logger.info(f"Model prediction (binary) - Student: {request.student_id}, "
                               f"Prob At-Risk: {prob_at_risk:.4f}, Prob Safe: {prob_safe:.4f}")
                    
                    probabilities = np.array([prob_safe, prob_at_risk])
                    prediction = 1 if prob_at_risk > 0.5 else 0
            else:
                # Demo mode prediction
                prediction, probabilities = self._demo_predict(request)

            # Determine risk level based on prediction
            if len(probabilities) == 3:
                # Multi-class
                risk_levels = ["Safe", "Medium Risk", "At-Risk"]
                risk_level = risk_levels[prediction]
                # Calculate weighted risk score: Medium Risk counts as 50% risk, At-Risk as 100% risk
                risk_score = float(probabilities[1] * 0.5 + probabilities[2] * 1.0)
                confidence = float(probabilities[prediction])
            else:
                # Binary
                risk_level = "At-Risk" if prediction == 1 else "Safe"
                risk_score = float(probabilities[1])  # Probability of being at-risk
                confidence = float(probabilities[prediction])

            # Generate recommendations
            recommendations = self._generate_recommendations(request, prediction, risk_score)

            # Get top risk factors
            top_risk_factors = self._get_top_risk_factors(request, prediction)

            # Create response with appropriate probabilities
            if len(probabilities) == 3:
                # Multi-class probabilities
                probs_dict = {
                    "Safe": float(probabilities[0]),
                    "Medium Risk": float(probabilities[1]),
                    "At-Risk": float(probabilities[2]),
                }
            else:
                # Binary probabilities
                probs_dict = {
                    "Safe": float(probabilities[0]),
                    "At-Risk": float(probabilities[1]),
                }
            
            response = AcademicRiskResponse(
                student_id=request.student_id,
                risk_level=risk_level,
                risk_score=risk_score,
                confidence=confidence,
                probabilities=probs_dict,
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
