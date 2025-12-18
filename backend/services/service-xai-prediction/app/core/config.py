from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # Service Configuration
    SERVICE_NAME: str = "XAI Prediction Service"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Base Directory
    @property
    def BASE_DIR(self) -> Path:
        return Path(__file__).parent.parent.parent
    
    # Model Directory
    @property
    def ML_MODELS_DIR(self) -> Path:
        """Get ML models directory with fallback logic"""
        # Try environment variable first
        env_path = os.getenv("ML_MODELS_PATH")
        if env_path:
            path = Path(env_path)
            if path.exists():
                return path
        
        # Development: relative path to ml/models
        dev_path = self.BASE_DIR.parent.parent.parent / "ml" / "models" / "xai_predictor"
        if dev_path.exists():
            return dev_path
        
        # Docker: models should be in /app/models
        docker_path = Path("/app/models")
        if docker_path.exists():
            return docker_path
        
        raise RuntimeError(f"ML models directory not found. Tried: {dev_path}, {docker_path}")
    
    # Model File Paths
    @property
    def MODEL_PATH(self) -> Path:
        return self.ML_MODELS_DIR / "student_model_best.joblib"
    
    @property
    def SCALER_PATH(self) -> Path:
        return self.ML_MODELS_DIR / "scaler_best.joblib"
    
    @property
    def ENCODER_PATH(self) -> Path:
        return self.ML_MODELS_DIR / "label_encoder_best.joblib"
    
    @property
    def FEATURES_PATH(self) -> Path:
        return self.ML_MODELS_DIR / "model_features_best.joblib"
    
    @property
    def METADATA_PATH(self) -> Path:
        return self.ML_MODELS_DIR / "model_metadata_best.joblib"
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://edumind.vercel.app"
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Database (if needed for storing predictions)
    DATABASE_URL: Optional[str] = None
    
    # Redis (for caching)
    REDIS_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()