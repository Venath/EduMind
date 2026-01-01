"""Schemas for XAI Prediction Service"""

# Academic risk schemas
from .academic_risk import AcademicRiskRequest, AcademicRiskResponse
from .health import HealthResponse, ModelInfoResponse
# Prediction schemas
from .prediction import (ExplanationResult, FeatureContribution,
                         PredictionRequest, PredictionResponse,
                         PredictionResult)

__all__ = [
    "HealthResponse",
    "ModelInfoResponse",
    "AcademicRiskRequest",
    "AcademicRiskResponse",
    "PredictionRequest",
    "PredictionResponse",
    "PredictionResult",
    "ExplanationResult",
    "FeatureContribution",
]
