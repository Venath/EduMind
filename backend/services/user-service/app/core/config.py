from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """User Service Settings"""

    SERVICE_NAME: str = "user-service"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database (optional for now)
    DATABASE_URL: Optional[str] = None

    # Security (optional for now)
    SECRET_KEY: str = "dev-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
