from typing import Optional

from pydantic_settings import BaseSettings


class BaseServiceSettings(BaseSettings):
    """Base settings for all microservices"""

    # Service Info
    SERVICE_NAME: str
    API_V1_STR: str = "/api/v1"

    # Environment
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        case_sensitive = True
        env_file = ".env"
