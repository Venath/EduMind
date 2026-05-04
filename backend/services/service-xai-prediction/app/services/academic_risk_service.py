import json
import logging
from pathlib import Path
from typing import List, Tuple

import numpy as np
import xgboost as xgb
from app.schemas.academic_risk import (
    AcademicRiskRequest,
    AcademicRiskResponse,
    CounterfactualChange,
    CounterfactualExplanation,
)

logger = logging.getLogger(__name__)

RISK_LEVELS = ["Safe", "Medium Risk", "At-Risk"]
RISK_LEVEL_RANK = {level: index for index, level in enumerate(RISK_LEVELS)}


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
                accuracy = self.metadata.get("metrics", {}).get("accuracy", 0)
                if not accuracy:
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

        if prediction == 2:  # At-Risk
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

        elif prediction == 1:  # Medium Risk
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

        else:  # Safe (prediction == 0)
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

    def _run_prediction_model_or_demo(
        self, request: AcademicRiskRequest
    ) -> Tuple[int, np.ndarray]:
        """Return the predicted class index and raw class probabilities."""
        if self.model is not None:
            dmatrix = self._prepare_features(request)
            raw_predictions = self.model.predict(dmatrix)

            if len(raw_predictions[0]) == 3:
                probabilities = np.array(
                    [
                        float(raw_predictions[0][0]),
                        float(raw_predictions[0][1]),
                        float(raw_predictions[0][2]),
                    ]
                )
                prediction = int(np.argmax(probabilities))
                logger.info(
                    "Model prediction (multi-class) - Student: %s, Prob Safe: %.4f, "
                    "Prob Medium: %.4f, Prob At-Risk: %.4f, Predicted: %s",
                    request.student_id,
                    probabilities[0],
                    probabilities[1],
                    probabilities[2],
                    prediction,
                )
                return prediction, probabilities

            prob_at_risk = float(raw_predictions[0])
            prob_at_risk = max(0.0, min(1.0, prob_at_risk))
            probabilities = np.array([1.0 - prob_at_risk, prob_at_risk])
            prediction = 1 if prob_at_risk > 0.5 else 0
            logger.info(
                "Model prediction (binary) - Student: %s, Prob At-Risk: %.4f, Prob Safe: %.4f",
                request.student_id,
                prob_at_risk,
                probabilities[0],
            )
            return prediction, probabilities

        return self._demo_predict(request)

    def _summarize_prediction(
        self, prediction: int, probabilities: np.ndarray
    ) -> tuple[str, float, float, dict[str, float]]:
        """Convert raw probabilities into the public response fields."""
        if len(probabilities) == 3:
            risk_level = RISK_LEVELS[prediction]
            risk_score = float(probabilities[1] * 0.5 + probabilities[2] * 1.0)
            confidence = float(probabilities[prediction])
            probs_dict = {
                "Safe": float(probabilities[0]),
                "Medium Risk": float(probabilities[1]),
                "At-Risk": float(probabilities[2]),
            }
            return risk_level, risk_score, confidence, probs_dict

        risk_level = "At-Risk" if prediction == 1 else "Safe"
        risk_score = float(probabilities[1])
        confidence = float(probabilities[prediction])
        probs_dict = {
            "Safe": float(probabilities[0]),
            "At-Risk": float(probabilities[1]),
        }
        return risk_level, risk_score, confidence, probs_dict

    def _normalize_request(self, request: AcademicRiskRequest) -> AcademicRiskRequest:
        """Keep derived binary flags consistent with the numeric features."""
        normalized = request.model_copy(deep=True)
        normalized.low_performance = 1 if normalized.avg_grade < 40 else 0
        normalized.low_engagement = 1 if normalized.assessment_completion_rate < 0.7 else 0
        normalized.has_previous_attempts = 1 if normalized.num_of_prev_attempts > 0 else 0
        return normalized

    def _format_feature_label(self, feature: str) -> str:
        labels = {
            "avg_grade": "average grade",
            "grade_consistency": "grade consistency",
            "grade_range": "grade range",
            "num_assessments": "assessment count",
            "assessment_completion_rate": "completion rate",
            "low_engagement": "low engagement flag",
        }
        return labels.get(feature, feature.replace("_", " "))

    def _build_candidate_updates(
        self, request: AcademicRiskRequest
    ) -> list[tuple[str, AcademicRiskRequest, str]]:
        """Generate one-step candidate changes for counterfactual search."""
        candidates: list[tuple[str, AcademicRiskRequest, str]] = []

        if request.avg_grade < 100:
            candidates.append(
                (
                    "avg_grade",
                    request.model_copy(
                        update={"avg_grade": round(min(100.0, request.avg_grade + 5.0), 1)}
                    ),
                    "Improving the average grade has the strongest direct effect on academic risk.",
                )
            )

        if request.grade_consistency < 100:
            candidates.append(
                (
                    "grade_consistency",
                    request.model_copy(
                        update={
                            "grade_consistency": round(
                                min(100.0, request.grade_consistency + 5.0), 1
                            )
                        }
                    ),
                    "More consistent performance reduces volatility-driven risk.",
                )
            )

        if request.grade_range > 0:
            candidates.append(
                (
                    "grade_range",
                    request.model_copy(
                        update={"grade_range": round(max(0.0, request.grade_range - 5.0), 1)}
                    ),
                    "Reducing the spread between scores makes performance more stable.",
                )
            )

        if request.num_assessments < 12:
            candidates.append(
                (
                    "num_assessments",
                    request.model_copy(update={"num_assessments": request.num_assessments + 1}),
                    "Completing more assessments gives the model stronger evidence of progress.",
                )
            )

        if request.assessment_completion_rate < 1.0:
            step = 0.1 if request.assessment_completion_rate < 0.7 else 0.05
            candidates.append(
                (
                    "assessment_completion_rate",
                    request.model_copy(
                        update={
                            "assessment_completion_rate": round(
                                min(1.0, request.assessment_completion_rate + step), 2
                            )
                        }
                    ),
                    "Higher assessment completion is one of the clearest signals of recovery.",
                )
            )

        if request.low_engagement == 1:
            candidates.append(
                (
                    "low_engagement",
                    request.model_copy(
                        update={
                            "assessment_completion_rate": round(
                                max(request.assessment_completion_rate, 0.75), 2
                            ),
                            "low_engagement": 0,
                        }
                    ),
                    "Removing the low-engagement flag requires the student to sustain a healthier completion pattern.",
                )
            )

        return candidates

    def _build_counterfactual(self, request: AcademicRiskRequest) -> CounterfactualExplanation:
        """Find a small set of changes that moves the student to a safer class."""
        base_request = self._normalize_request(request)
        prediction, probabilities = self._run_prediction_model_or_demo(base_request)
        current_outcome, current_score, current_confidence, _ = self._summarize_prediction(
            prediction, probabilities
        )

        if current_outcome == "Safe":
            return CounterfactualExplanation(
                current_outcome="Safe",
                target_outcome="Safe",
                achievable=True,
                summary="This student is already in the safest outcome band. Focus on maintaining the current performance pattern.",
                estimated_risk_level="Safe",
                estimated_risk_score=current_score,
                estimated_confidence=current_confidence,
                changes=[],
            )

        target_outcomes = ["Safe"]
        if len(probabilities) == 3 and current_outcome == "At-Risk":
            target_outcomes.append("Medium Risk")

        best_partial: CounterfactualExplanation | None = None
        for target_outcome in target_outcomes:
            target_rank = RISK_LEVEL_RANK[target_outcome]
            working_request = base_request
            working_prediction = prediction
            working_probabilities = probabilities
            working_outcome = current_outcome
            working_score = current_score
            working_confidence = current_confidence
            changes: dict[str, CounterfactualChange] = {}

            for _ in range(8):
                best_option: tuple[
                    str,
                    AcademicRiskRequest,
                    str,
                    int,
                    np.ndarray,
                    str,
                    float,
                    float,
                ] | None = None

                for feature, candidate_request, rationale in self._build_candidate_updates(
                    working_request
                ):
                    candidate_request = self._normalize_request(candidate_request)
                    candidate_prediction, candidate_probabilities = self._run_prediction_model_or_demo(
                        candidate_request
                    )
                    candidate_outcome, candidate_score, candidate_confidence, _ = (
                        self._summarize_prediction(candidate_prediction, candidate_probabilities)
                    )

                    current_rank = RISK_LEVEL_RANK[working_outcome]
                    candidate_rank = RISK_LEVEL_RANK[candidate_outcome]
                    is_better = candidate_rank < current_rank or (
                        candidate_rank == current_rank and candidate_score < working_score - 1e-6
                    )
                    if not is_better:
                        continue

                    if best_option is None or (
                        candidate_rank,
                        candidate_score,
                    ) < (
                        RISK_LEVEL_RANK[best_option[5]],
                        best_option[6],
                    ):
                        best_option = (
                            feature,
                            candidate_request,
                            rationale,
                            candidate_prediction,
                            candidate_probabilities,
                            candidate_outcome,
                            candidate_score,
                            candidate_confidence,
                        )

                if best_option is None:
                    break

                (
                    feature,
                    working_request,
                    rationale,
                    working_prediction,
                    working_probabilities,
                    working_outcome,
                    working_score,
                    working_confidence,
                ) = best_option

                original_value = getattr(base_request, feature)
                suggested_value = getattr(working_request, feature)
                direction = "maintain"
                delta: float | None = None
                if isinstance(original_value, (int, float)) and isinstance(
                    suggested_value, (int, float)
                ):
                    delta = round(float(suggested_value) - float(original_value), 2)
                    if delta > 0:
                        direction = "increase"
                    elif delta < 0:
                        direction = "decrease"
                elif original_value != suggested_value:
                    direction = "toggle"

                changes[feature] = CounterfactualChange(
                    feature=feature,
                    current_value=original_value,
                    suggested_value=suggested_value,
                    direction=direction,
                    delta=delta,
                    rationale=rationale,
                )

                if RISK_LEVEL_RANK[working_outcome] <= target_rank:
                    break

            ordered_changes = list(changes.values())
            achieved_target = RISK_LEVEL_RANK[working_outcome] <= target_rank

            if ordered_changes:
                lead_change_text = ", ".join(
                    f"{self._format_feature_label(change.feature)} to {change.suggested_value}"
                    for change in ordered_changes[:2]
                )
            else:
                lead_change_text = "no feasible feature changes"

            summary = (
                f"Adjust {lead_change_text} to move this student from "
                f"{current_outcome} toward {target_outcome}."
                if ordered_changes
                else f"No realistic low-step path was found from {current_outcome} to {target_outcome} with the current feature set."
            )

            explanation = CounterfactualExplanation(
                current_outcome=current_outcome,
                target_outcome=target_outcome,
                achievable=achieved_target,
                summary=summary,
                estimated_risk_level=working_outcome,
                estimated_risk_score=working_score,
                estimated_confidence=working_confidence,
                changes=ordered_changes,
            )

            if achieved_target:
                return explanation

            if best_partial is None:
                best_partial = explanation
            elif explanation.estimated_risk_level is not None and best_partial.estimated_risk_level is not None:
                candidate_key = (
                    RISK_LEVEL_RANK[explanation.estimated_risk_level],
                    explanation.estimated_risk_score or 1.0,
                )
                best_key = (
                    RISK_LEVEL_RANK[best_partial.estimated_risk_level],
                    best_partial.estimated_risk_score or 1.0,
                )
                if candidate_key < best_key:
                    best_partial = explanation

        return best_partial or CounterfactualExplanation(
            current_outcome=current_outcome,
            target_outcome="Safe",
            achievable=False,
            summary="No realistic counterfactual path could be generated for this student with the available features.",
            estimated_risk_level=current_outcome,
            estimated_risk_score=current_score,
            estimated_confidence=current_confidence,
            changes=[],
        )

    async def predict(self, request: AcademicRiskRequest) -> AcademicRiskResponse:
        """Make academic risk prediction."""
        try:
            normalized_request = self._normalize_request(request)
            prediction, probabilities = self._run_prediction_model_or_demo(normalized_request)
            risk_level, risk_score, confidence, probs_dict = self._summarize_prediction(
                prediction, probabilities
            )

            response = AcademicRiskResponse(
                student_id=normalized_request.student_id,
                risk_level=risk_level,
                risk_score=risk_score,
                confidence=confidence,
                probabilities=probs_dict,
                recommendations=self._generate_recommendations(
                    normalized_request, prediction, risk_score
                ),
                top_risk_factors=self._get_top_risk_factors(
                    normalized_request, prediction
                ),
                counterfactual=self._build_counterfactual(normalized_request),
            )

            logger.info(
                "Prediction for %s: %s (confidence: %.2f%%)",
                normalized_request.student_id,
                risk_level,
                confidence * 100,
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
