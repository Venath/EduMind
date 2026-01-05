"""
Shared prediction schemas for backend services.
These schemas can be imported by any backend service that needs prediction types.
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PredictionType(str, Enum):
    """Type of prediction method used."""
    ML_MODEL = "ml_model"
    HEURISTIC = "heuristic"
    BLENDED = "blended"


# ============================================
# Prediction Request/Response
# ============================================

class PredictionRequest(BaseModel):
    """Request schema for student outcome prediction."""
    student_id: str = Field(..., description="Unique student identifier")
    total_interactions: float = Field(default=0.0, ge=0)
    avg_response_time: float = Field(default=0.0, ge=0)
    consistency_score: float = Field(default=0.5, ge=0, le=1)
    days_inactive: int = Field(default=0, ge=0)
    completion_rate: float = Field(default=0.5, ge=0, le=1)
    assessment_score: float = Field(default=50.0, ge=0, le=100)


class PredictionResult(BaseModel):
    """Individual prediction result."""
    predicted_class: str
    probability: float = Field(..., ge=0, le=1)
    risk_level: str


class FeatureContribution(BaseModel):
    """Feature importance for explanation."""
    feature: str
    value: float
    contribution: float
    impact: str  # positive or negative


class ExplanationResult(BaseModel):
    """XAI Explanation result."""
    feature_contributions: List[FeatureContribution]
    top_positive_factors: List[str]
    top_negative_factors: List[str]
    shap_values: Optional[Dict[str, float]] = None
    base_value: Optional[float] = None


class PredictionResponse(BaseModel):
    """Response schema for prediction."""
    prediction: PredictionResult
    explanation: ExplanationResult
    recommendations: List[str] = Field(default_factory=list)


# ============================================
# Academic Risk Request/Response
# ============================================

class AcademicRiskRequest(BaseModel):
    """Request schema for academic risk prediction."""
    student_id: str
    code_module: Optional[str] = None
    code_presentation: Optional[str] = None
    total_clicks: int = Field(default=0, ge=0)
    days_active: int = Field(default=0, ge=0)
    avg_score: float = Field(default=0.0, ge=0, le=100)
    studied_credits: Optional[int] = Field(default=60, ge=0, le=300)
    num_of_prev_attempts: Optional[int] = Field(default=0, ge=0, le=10)


class AcademicRiskResponse(BaseModel):
    """Response schema for academic risk prediction."""
    student_id: str
    risk_level: str
    risk_probability: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    prediction_details: Dict[str, float]
    feature_importance: Dict[str, float]
    risk_factors: List[str]
    recommendations: List[str]
    timestamp: str


# ============================================
# Smart Prediction Request/Response
# ============================================

class DataQuality(BaseModel):
    """Information about data quality."""
    status: str  # sufficient, partial, insufficient
    ml_ready: bool
    completeness_score: float
    missing_for_ml: Dict[str, int]
    message: str


class SmartPredictionRequest(BaseModel):
    """Combined request for smart prediction."""
    student_id: str
    total_clicks: int = Field(default=0, ge=0)
    days_active: int = Field(default=0, ge=0)
    avg_score: float = Field(default=0.0, ge=0, le=100)
    studied_credits: int = Field(default=60, ge=0, le=300)
    num_of_prev_attempts: int = Field(default=0, ge=0, le=10)
    previous_gpa: Optional[float] = Field(default=None, ge=0, le=4)
    entrance_score: Optional[float] = Field(default=None, ge=0, le=100)
    previous_education: Optional[str] = None
    expected_weekly_hours: Optional[int] = Field(default=None, ge=0, le=80)
    days_before_start: Optional[int] = None
    code_module: Optional[str] = None
    code_presentation: Optional[str] = None


class SmartPredictionResponse(BaseModel):
    """Response from smart prediction."""
    student_id: str
    risk_level: str
    risk_probability: float
    confidence: float
    prediction_type: str
    data_quality: DataQuality
    risk_factors: List[str]
    protective_factors: List[str] = []
    recommendations: List[str]
    feature_importance: Optional[Dict[str, float]] = None
    timestamp: str
    note: str
