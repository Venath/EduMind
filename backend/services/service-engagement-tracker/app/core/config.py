"""
Configuration settings for Engagement Tracker Service
"""
from backend.shared.config import BaseServiceSettings
from typing import Optional

class Settings(BaseServiceSettings):
    """Application settings loaded from environment variables"""
    
    # Service identification
    SERVICE_NAME: str = "engagement-tracker-service"
    DESCRIPTION: str = "Tracks student engagement and provides intervention recommendations"
    
    # Database (using psycopg3 driver)
    DATABASE_URL: str = "postgresql+psycopg://postgres:admin@localhost:5432/edumind_venath"
    
    # API Configuration
    @property
    def API_V1_PREFIX(self) -> str:
        return self.API_PREFIX
    
    # CORS
    @property
    def CORS_ORIGINS(self) -> list:
        return self.ALLOWED_ORIGINS
    
    # Engagement Scoring Weights
    WEIGHT_LOGIN_FREQUENCY: float = 0.25
    WEIGHT_SESSION_DURATION: float = 0.20
    WEIGHT_CONTENT_INTERACTION: float = 0.25
    WEIGHT_FORUM_PARTICIPATION: float = 0.15
    WEIGHT_ASSIGNMENT_COMPLETION: float = 0.15
    
    # Engagement Thresholds
    ENGAGEMENT_THRESHOLD_LOW: float = 40.0
    ENGAGEMENT_THRESHOLD_HIGH: float = 70.0
    
    # ML Model Settings
    MODEL_PATH: str = "ml/models/engagement_predictor/artifacts"
    MODEL_VERSION: str = "v1.0"
    PREDICTION_HORIZON_DAYS: int = 7
    
    # Risk Level Thresholds
    RISK_THRESHOLD_LOW: float = 0.3
    RISK_THRESHOLD_HIGH: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

