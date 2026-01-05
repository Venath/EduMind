"""
EduMind Engagement Tracking Service - FastAPI Application

Complete API for student engagement tracking and disengagement prediction
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Import routers
from app.api import routes_system
from app.api import routes_engagement
from app.api import routes_predictions
from app.api import routes_students
from app.api import routes_events
from app.api import routes_scheduling

# Create FastAPI app
app = FastAPI(
    title="EduMind Engagement Tracking Service",
    version="1.0.0",
    description="""
    ## 🎓 EduMind Engagement Tracking API
    
    Track student engagement, predict disengagement risk, and trigger interventions.
    
    ### Features
    - 📊 Real-time engagement scoring
    - 🎯 ML-powered disengagement prediction (99.94% accuracy)
    - 📈 Student analytics and dashboards
    - 🚨 At-risk student identification
    - 📥 Event ingestion from Moodle/LMS
    
    ### Key Endpoints
    - **Engagement**: `/api/v1/engagement` - Get engagement scores
    - **Predictions**: `/api/v1/predictions` - Get risk predictions
    - **Students**: `/api/v1/students` - Student analytics
    - **Events**: `/api/v1/events` - Ingest activity events
    
    ### ML Models
    - **Engagement Scoring**: Weighted composite (5 components)
    - **Disengagement Prediction**: Gradient Boosting (99.94% accuracy, 0.9991 ROC-AUC)
    """,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    contact={
        "name": "EduMind Development Team",
        "email": "support@edumind.example.com"
    },
    license_info={
        "name": "MIT License"
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_system.router)
app.include_router(routes_engagement.router)
app.include_router(routes_predictions.router)
app.include_router(routes_students.router)
app.include_router(routes_events.router)
app.include_router(routes_scheduling.router)

# Favicon endpoint to prevent 404 errors (must be before static files)
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Return empty favicon to prevent 404 errors"""
    from fastapi.responses import Response
    return Response(content=b"", media_type="image/x-icon")


# Chrome DevTools endpoint to prevent 404 errors
@app.get("/.well-known/appspecific/com.chrome.devtools.json", include_in_schema=False)
async def chrome_devtools():
    """Return empty response for Chrome DevTools to prevent 404 errors"""
    from fastapi.responses import Response
    return Response(content=b"{}", media_type="application/json")


# Source map endpoint to prevent 404 errors (must be before static files)
@app.get("/app/{filename}.map", include_in_schema=False)
async def source_map(filename: str):
    """Return empty source map to prevent 404 errors"""
    from fastapi.responses import Response
    return Response(content=b"{}", media_type="application/json")


# Mount static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

# Redirect root to frontend app
@app.get("/", include_in_schema=False)
async def redirect_to_app():
    """Redirect root to frontend application"""
    return RedirectResponse(url="/app/index.html")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Runs when the application starts"""
    print("EduMind Engagement Tracking Service starting...")
    print("API Documentation: http://localhost:8002/api/docs")
    print("Service ready!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Runs when the application shuts down"""
    print("EduMind Engagement Tracking Service shutting down...")
