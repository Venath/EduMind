"""Learning Style Recognition Service - FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EduMind Learning Style Recognition Service",
    version="1.0.0",
    description="Classifies learning styles based on student behavior",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"service": "Learning Style Recognition Service", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "learning-style-service"}


@app.post("/api/v1/classify")
async def classify_learning_style(data: dict):
    return {
        "learning_style": None,
        "confidence": None,
        "message": "Learning style classification endpoints coming soon",
    }
