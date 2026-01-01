"""
Prediction Schemas for XAI Prediction Service
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Request schema for student outcome prediction"""

    student_id: str = Field(..., description="Unique student identifier")

    # Core academic features
    total_interactions: float = Field(
        default=0.0, ge=0, description="Total learning interactions"
    )
    avg_response_time: float = Field(
        default=0.0, ge=0, description="Average response time in seconds"
    )
    consistency_score: float = Field(
        default=0.5, ge=0, le=1, description="Learning consistency (0-1)"
    )
    days_inactive: int = Field(default=0, ge=0, description="Days since last activity")

    # Optional features
    completion_rate: float = Field(
        default=0.5, ge=0, le=1, description="Course completion rate"
    )
    assessment_score: float = Field(
        default=50.0, ge=0, le=100, description="Average assessment score"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "student_id": "student_12345",
                "total_interactions": 150,
                "avg_response_time": 45.5,
                "consistency_score": 0.75,
                "days_inactive": 3,
                "completion_rate": 0.65,
                "assessment_score": 72.5,
            }
        }
    }


class PredictionResult(BaseModel):
    """Individual prediction result"""

    predicted_class: str = Field(..., description="Predicted outcome class")
    probability: float = Field(..., ge=0, le=1, description="Prediction probability")
    risk_level: str = Field(..., description="Risk level: low, medium, high")


class FeatureContribution(BaseModel):
    """Feature importance for explanation"""

    feature: str
    value: float
    contribution: float
    impact: str  # positive or negative


class ExplanationResult(BaseModel):
    """XAI Explanation result"""

    feature_contributions: List[FeatureContribution]
    top_positive_factors: List[str]
    top_negative_factors: List[str]
    shap_values: Optional[Dict[str, float]] = None
    base_value: Optional[float] = None


class PredictionResponse(BaseModel):
    """Response schema for prediction"""

    prediction: PredictionResult
    explanation: ExplanationResult
    recommendations: List[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "prediction": {
                    "predicted_class": "at_risk",
                    "probability": 0.75,
                    "risk_level": "high",
                },
                "explanation": {
                    "feature_contributions": [
                        {
                            "feature": "days_inactive",
                            "value": 15,
                            "contribution": 0.25,
                            "impact": "negative",
                        },
                        {
                            "feature": "total_interactions",
                            "value": 50,
                            "contribution": 0.15,
                            "impact": "negative",
                        },
                    ],
                    "top_positive_factors": ["consistency_score"],
                    "top_negative_factors": ["days_inactive", "total_interactions"],
                },
                "recommendations": [
                    "Increase engagement with course materials",
                    "Complete pending assessments",
                ],
            }
        }
    }
