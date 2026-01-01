from typing import Optional

from app.core.logging import configure_logging, get_logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "course-service"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: Optional[str] = None
    SECRET_KEY: str = "dev-secret-key"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
configure_logging(log_level=settings.LOG_LEVEL)
logger = get_logger(__name__)

app = FastAPI(title=settings.SERVICE_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}
