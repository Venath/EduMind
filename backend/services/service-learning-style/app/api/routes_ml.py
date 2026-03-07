"""
Machine Learning API Routes

REST API endpoints for learning style classification using ML.

ENDPOINTS:
1. POST /ml/classify/{student_id} - Classify single student
2. POST /ml/classify-batch - Classify all students
3. GET /ml/model-info - Get model information
4. POST /ml/retrain - Trigger model retraining

Author: Subasinghe S A V R (IT22325846)
"""

import httpx
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List
from pydantic import BaseModel

from app.api.dependencies import get_db
from app.core.config import settings
from app.services.ml_service import get_ml_service
from app.services.engagement_sync_service import sync_student_behavior


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================

class PredictionResponse(BaseModel):
    """Response schema for learning style prediction."""
    student_id: str
    predicted_style: str
    confidence: float
    confidence_level: str
    probabilities: Dict[str, float]
    days_tracked: int
    model_version: str
    predicted_at: str


class BatchPredictionResponse(BaseModel):
    """Response schema for batch classification."""
    total_students: int
    classified: int
    insufficient_data: int
    errors: int
    predictions: List[Dict]


class ModelInfoResponse(BaseModel):
    """Response schema for model information."""
    status: str
    model_type: str = None
    num_features: int = None
    classes: List[str] = None
    version: str = None
    training_date: str = None
    accuracy: float = None
    num_training_samples: int = None


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    error: str
    message: str
    details: Dict = None


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/classify/{student_id}", response_model=PredictionResponse)
async def classify_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    Classify a single student's learning style using ML.
    
    **Requirements:**
    - Student must have at least 7 days of behavior tracking data
    - ML model must be trained and loaded
    
    **Returns:**
    - Predicted learning style (Visual, Auditory, Reading, Kinesthetic, Mixed)
    - Confidence score (0.0 to 1.0)
    - Probability distribution across all styles
    - Number of days tracked
    
    **Example Response:**
    ```json
    {
      "student_id": "STU0001",
      "predicted_style": "Visual",
      "confidence": 0.87,
      "confidence_level": "High",
      "probabilities": {
        "Visual": 0.87,
        "Auditory": 0.05,
        "Reading": 0.04,
        "Kinesthetic": 0.03,
        "Mixed": 0.01
      },
      "days_tracked": 14,
      "model_version": "1.0",
      "predicted_at": "2025-12-28T10:30:00"
    }
    ```
    
    **Error Cases:**
    - 404: Student not found
    - 400: Insufficient data (< 7 days)
    - 503: Model not available
    """
    # Get ML service
    ml_service = get_ml_service()
    
    # Make prediction
    result = ml_service.predict_learning_style(student_id, db)
    
    # Handle errors
    if 'error' in result:
        if result['error'] == 'Insufficient data':
            raise HTTPException(
                status_code=400,
                detail={
                    'error': result['error'],
                    'message': result['message'],
                    'days_tracked': result.get('days_tracked', 0),
                    'min_required': result.get('min_required', 7)
                }
            )
        elif result['error'] == 'Model not available':
            raise HTTPException(
                status_code=503,
                detail={
                    'error': result['error'],
                    'message': result['message']
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    'error': result['error'],
                    'message': result.get('message', 'Unknown error')
                }
            )
    
    return result


def _refresh_behavior_from_engagement(student_id: str) -> None:
    """
    Ensure learning-style has the latest behavior data before classification.
    1. Trigger engagement-tracker to aggregate today and yesterday (covers timezone/timing).
    2. Sync those metrics into this service's StudentBehaviorTracking.
    """
    from datetime import date, timedelta
    base = settings.ENGAGEMENT_API_URL.rstrip("/")
    try:
        with httpx.Client(timeout=15.0) as client:
            for days_ago in (0, 1, 2):
                d = date.today() - timedelta(days=days_ago)
                client.post(
                    f"{base}/aggregation/process/{student_id}",
                    params={"institute_id": "LMS_INST_A", "target_date": str(d)},
                )
    except Exception:
        pass
    try:
        sync_student_behavior(student_id=student_id, days=14)
    except Exception:
        pass


@router.post("/classify-and-update/{student_id}", response_model=PredictionResponse)
async def classify_and_update_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    Classify a student's learning style and update their profile.
    
    This endpoint:
    1. Refreshes behavior from engagement-tracker (aggregate + sync) so latest LMS activity is included
    2. Predicts the learning style using ML
    3. Updates the student's profile with the prediction
    4. Returns the prediction result
    
    **Use this when you want to permanently update the student's profile.**
    
    **Returns:** Same as /classify/{student_id}
    """
    _refresh_behavior_from_engagement(student_id)
    ml_service = get_ml_service()
    result = ml_service.classify_and_update(student_id, db)
    
    # Handle errors (same as classify endpoint)
    if 'error' in result:
        if result['error'] == 'Insufficient data':
            raise HTTPException(status_code=400, detail=result)
        elif result['error'] == 'Model not available':
            raise HTTPException(status_code=503, detail=result)
        else:
            raise HTTPException(status_code=500, detail=result)
    
    return result


@router.post("/classify-batch", response_model=BatchPredictionResponse)
async def classify_batch(
    min_days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Classify all students with sufficient data.
    
    **Batch Processing:**
    - Processes all students in the database
    - Only classifies students with >= min_days of data
    - Updates all student profiles automatically
    - Returns summary statistics
    
    **Query Parameters:**
    - `min_days` (optional): Minimum days of data required (default: 7)
    
    **Returns:**
    - Total students processed
    - Number successfully classified
    - Number with insufficient data
    - Number of errors
    - List of all predictions
    
    **Example Response:**
    ```json
    {
      "total_students": 30,
      "classified": 28,
      "insufficient_data": 2,
      "errors": 0,
      "predictions": [
        {
          "student_id": "STU0001",
          "style": "Visual",
          "confidence": 0.87
        },
        ...
      ]
    }
    ```
    
    **Use Case:**
    - Nightly batch jobs
    - Initial classification of all students
    - Re-classification after model retraining
    """
    # Get ML service
    ml_service = get_ml_service()
    
    # Check if model is available
    model_info = ml_service.get_model_info()
    if model_info['status'] != 'loaded':
        raise HTTPException(
            status_code=503,
            detail={
                'error': 'Model not available',
                'message': 'ML model not trained yet. Please train model first.'
            }
        )
    
    # Run batch classification
    result = ml_service.batch_classify(db, min_days)
    
    return result


@router.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info():
    """
    Get information about the loaded ML model.
    
    **Returns:**
    - Model status (loaded/not_loaded)
    - Model type (e.g., RandomForestClassifier)
    - Number of features used
    - Classes (learning styles)
    - Version
    - Training date
    - Test accuracy
    - Number of training samples
    
    **Example Response:**
    ```json
    {
      "status": "loaded",
      "model_type": "RandomForestClassifier",
      "num_features": 24,
      "classes": ["Visual", "Auditory", "Reading", "Kinesthetic", "Mixed"],
      "version": "1.0",
      "training_date": "2025-12-28T10:00:00",
      "accuracy": 0.79,
      "num_training_samples": 120
    }
    ```
    
    **Use Case:**
    - Check if model is ready
    - Display model statistics in admin dashboard
    - Verify model version
    """
    ml_service = get_ml_service()
    info = ml_service.get_model_info()
    
    return info


@router.post("/retrain")
async def retrain_model(
    background_tasks: BackgroundTasks,
    algorithm: str = "random_forest",
    tune_hyperparameters: bool = False
):
    """
    Trigger model retraining (runs in background).
    
    **WARNING:** This is a long-running operation (5-30 minutes).
    
    **Query Parameters:**
    - `algorithm`: 'random_forest' or 'gradient_boosting' (default: random_forest)
    - `tune_hyperparameters`: Whether to perform grid search (default: false)
    
    **Returns:**
    - Message confirming training started
    - Training will run in background
    
    **Example Response:**
    ```json
    {
      "message": "Model retraining started in background",
      "algorithm": "random_forest",
      "tune_hyperparameters": false,
      "estimated_time": "5-10 minutes"
    }
    ```
    
    **Use Case:**
    - After adding new training data
    - Periodic model updates (weekly/monthly)
    - Experimenting with different algorithms
    
    **Note:** Check logs for training progress and results.
    """
    # Validate algorithm
    if algorithm not in ['random_forest', 'gradient_boosting']:
        raise HTTPException(
            status_code=400,
            detail={
                'error': 'Invalid algorithm',
                'message': f"Algorithm must be 'random_forest' or 'gradient_boosting', got '{algorithm}'"
            }
        )
    
    # Add training task to background
    def train_task():
        """Background task for model training."""
        try:
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent.parent))
            
            from ml.train_learning_style_model import LearningStyleModelTrainer
            
            print(f"\n[Background Task] Starting model training...")
            print(f"[Background Task]   Algorithm: {algorithm}")
            print(f"[Background Task]   Tune hyperparameters: {tune_hyperparameters}")
            
            trainer = LearningStyleModelTrainer()
            model, accuracy = trainer.train_pipeline(
                algorithm=algorithm,
                tune_hyperparameters=tune_hyperparameters,
                version='1.1'  # Increment version
            )
            
            print(f"[Background Task] Training complete! Accuracy: {accuracy:.4f}")
            
            # Reload model in ML service
            ml_service = get_ml_service()
            ml_service._load_model()
            
        except Exception as e:
            print(f"[Background Task] ERROR during training: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Add to background tasks
    background_tasks.add_task(train_task)
    
    # Estimate time
    estimated_time = "15-30 minutes" if tune_hyperparameters else "5-10 minutes"
    
    return {
        "message": "Model retraining started in background",
        "algorithm": algorithm,
        "tune_hyperparameters": tune_hyperparameters,
        "estimated_time": estimated_time,
        "note": "Check server logs for training progress"
    }


@router.get("/feature-importance")
async def get_feature_importance():
    """
    Get feature importance from the trained model.
    
    **Returns:**
    - List of features ranked by importance
    - Importance scores (0.0 to 1.0)
    
    **Example Response:**
    ```json
    {
      "features": [
        {
          "feature": "visual_preference_score",
          "importance": 0.1234
        },
        {
          "feature": "reading_time_ratio",
          "importance": 0.0987
        },
        ...
      ]
    }
    ```
    
    **Use Case:**
    - Understand which behaviors are most predictive
    - Explain model decisions
    - Feature selection for model improvement
    """
    ml_service = get_ml_service()
    
    # Check if model is loaded
    if ml_service.model is None:
        raise HTTPException(
            status_code=503,
            detail={
                'error': 'Model not available',
                'message': 'ML model not trained yet.'
            }
        )
    
    # Get feature importance from metadata
    if ml_service.metadata and 'feature_importance' in ml_service.metadata:
        features = ml_service.metadata['feature_importance']
        
        # Sort by importance
        features_sorted = sorted(features, key=lambda x: x['importance'], reverse=True)
        
        return {
            'features': features_sorted[:20],  # Top 20
            'total_features': len(features)
        }
    else:
        raise HTTPException(
            status_code=404,
            detail={
                'error': 'Feature importance not available',
                'message': 'Model metadata does not contain feature importance.'
            }
        )


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get("/health")
async def ml_health_check():
    """
    Check if ML service is healthy and ready.
    
    **Returns:**
    - Service status
    - Model status
    - Ready for predictions (boolean)
    """
    ml_service = get_ml_service()
    model_info = ml_service.get_model_info()
    
    is_ready = model_info['status'] == 'loaded'
    
    return {
        'service': 'ML Classification Service',
        'status': 'healthy',
        'model_loaded': is_ready,
        'ready_for_predictions': is_ready,
        'model_type': model_info.get('model_type'),
        'model_version': model_info.get('version')
    }






