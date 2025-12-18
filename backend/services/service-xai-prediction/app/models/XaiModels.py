from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PredictionRequest(BaseModel):
    """Request schema for student outcome prediction"""
    student_id: UUID
    features: Dict[str, float]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "student_id": "123e4567-e89b-12d3-a456-426614174000",
                "features": {
                    "code_module": 0,
                    "code_presentation": 1,
                    "gender": 0,
                    "region": 5,
                    "highest_education": 2,
                    "imd_band": 50,
                    "age_band": 2,
                    "num_of_prev_attempts": 0,
                    "studied_credits": 120,
                    "disability": 0
                }
            }
        }
    }

class FeatureImportance(BaseModel):
    """Feature importance details"""
    feature_name: str
    importance: float
    shap_value: float
    contribution: str

class Explanation(BaseModel):
    """Explanation schema for XAI predictions"""
    id: UUID = Field(default_factory=uuid4)
    prediction_result_id: UUID
    shap_values: Dict[str, float]
    top_features: List[FeatureImportance]
    natural_language_explanation: str
    confidence_factors: List[str]
    risk_factors: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PredictionResult(BaseModel):
    """Prediction result schema"""
    id: UUID = Field(default_factory=uuid4)
    request_id: UUID
    student_id: UUID
    predicted_class: str
    probability: float
    probabilities: Dict[str, float]
    risk_level: RiskLevel
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PredictionResponse(BaseModel):
    """Complete prediction response with explanation"""
    prediction: PredictionResult
    explanation: Explanation