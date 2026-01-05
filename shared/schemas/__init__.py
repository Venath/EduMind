"""
Shared schemas for backend services.
"""

from .prediction import (
    AcademicRiskRequest,
    AcademicRiskResponse,
    DataQuality,
    ExplanationResult,
    FeatureContribution,
    PredictionRequest,
    PredictionResponse,
    PredictionResult,
    PredictionType,
    RiskLevel,
    SmartPredictionRequest,
    SmartPredictionResponse,
)

__all__ = [
    "RiskLevel",
    "PredictionType",
    "PredictionRequest",
    "PredictionResult",
    "FeatureContribution",
    "ExplanationResult",
    "PredictionResponse",
    "AcademicRiskRequest",
    "AcademicRiskResponse",
    "DataQuality",
    "SmartPredictionRequest",
    "SmartPredictionResponse",
]
