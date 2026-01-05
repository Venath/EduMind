"""
Configuration settings for Engagement Tracker Service
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Service identification
    SERVICE_NAME: str = "engagement-tracker-service"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Tracks student engagement and provides intervention recommendations"
    
    # Database (using psycopg3 driver)
    DATABASE_URL: str = "postgresql+psycopg://postgres:admin@localhost:5432/edumind"
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
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

