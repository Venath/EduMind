from typing import Any, Dict, List

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response schema"""

    status: str
    service: str
    version: str
    model_loaded: bool


class ModelInfoResponse(BaseModel):
    """Model information response schema"""

    model_type: str
    features_count: int
    feature_names: List[str]
    classes: List[str]
    metadata: Dict[str, Any]
