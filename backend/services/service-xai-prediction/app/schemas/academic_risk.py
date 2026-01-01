"""
Academic Risk Prediction Schemas for OULAD Model
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AcademicRiskRequest(BaseModel):
    """Request schema for academic risk prediction"""

    student_id: str
    avg_grade: float = Field(
        ..., ge=0, le=100, description="Average assessment score (0-100)"
    )
    grade_consistency: float = Field(
        ..., ge=0, le=100, description="Performance consistency score"
    )
    grade_range: float = Field(
        ..., ge=0, le=100, description="Score variability (max - min)"
    )
    num_assessments: int = Field(
        ..., ge=0, description="Number of assessments completed"
    )
    assessment_completion_rate: float = Field(
        ..., ge=0, le=1, description="Completion rate (0-1)"
    )
    studied_credits: int = Field(..., ge=0, description="Course credits enrolled")
    num_of_prev_attempts: int = Field(
        ..., ge=0, description="Number of previous attempts"
    )
    low_performance: int = Field(..., ge=0, le=1, description="Binary: grade < 40%")
    low_engagement: int = Field(
        ..., ge=0, le=1, description="Binary: low assessment completion"
    )
    has_previous_attempts: int = Field(
        ..., ge=0, le=1, description="Binary: has failed before"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "student_id": "student_12345",
                "avg_grade": 65.5,
                "grade_consistency": 85.2,
                "grade_range": 30.0,
                "num_assessments": 8,
                "assessment_completion_rate": 0.8,
                "studied_credits": 60,
                "num_of_prev_attempts": 0,
                "low_performance": 0,
                "low_engagement": 0,
                "has_previous_attempts": 0,
            }
        }
    }


class AcademicRiskResponse(BaseModel):
    """Response schema for academic risk prediction"""

    student_id: str
    risk_level: str = Field(..., description="Safe or At-Risk")
    risk_score: float = Field(
        ..., ge=0, le=1, description="Probability of being at-risk"
    )
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")
    probabilities: dict = Field(..., description="Probabilities for each class")
    recommendations: List[str] = Field(..., description="Personalized recommendations")
    top_risk_factors: List[dict] = Field(
        ..., description="Top factors contributing to risk"
    )
    prediction_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_schema_extra": {
            "example": {
                "student_id": "student_12345",
                "risk_level": "At-Risk",
                "risk_score": 0.847,
                "confidence": 0.847,
                "probabilities": {"Safe": 0.153, "At-Risk": 0.847},
                "recommendations": [
                    "Seek immediate tutoring - grade is critically low",
                    "Complete all remaining assessments",
                    "Contact academic advisor immediately",
                ],
                "top_risk_factors": [
                    {"feature": "avg_grade", "value": 35.5, "impact": "high"},
                    {"feature": "num_assessments", "value": 3, "impact": "high"},
                ],
                "prediction_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-15T10:30:00",
            }
        }
    }
