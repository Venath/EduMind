from app.core.config import settings
from app.core.logging import get_logger
from app.schemas import (HealthResponse, ModelInfoResponse, PredictionRequest,
                         PredictionResponse)
from app.Services.ml_service import ml_service
from fastapi import APIRouter, HTTPException, status

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        model_loaded=ml_service.model is not None,
    )


@router.post(
    "/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK
)
async def predict_student_outcome(request: PredictionRequest):
    """
    Predict student academic outcome with explainable AI

    Args:
        request: Student features for prediction

    Returns:
        Prediction result with XAI explanation
    """
    try:
        logger.info(f"Prediction request for student: {request.student_id}")

        # Make prediction
        prediction, explanation = await ml_service.predict(request)

        # Generate recommendations
        recommendations = ml_service._generate_recommendations(
            request, prediction.risk_level
        )

        # Return response
        response = PredictionResponse(
            prediction=prediction,
            explanation=explanation,
            recommendations=recommendations,
        )

        logger.info(
            f"Prediction complete: {prediction.predicted_class} "
            f"(probability: {prediction.probability:.2%}, risk: {prediction.risk_level})"
        )

        return response

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


@router.get("/model/info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get information about the loaded ML model"""
    try:
        return ModelInfoResponse(
            model_type="XGBoost Classifier with SHAP Explanations",
            features_count=len(ml_service.feature_names),
            feature_names=ml_service.feature_names,
            classes=ml_service.label_encoder.classes_.tolist(),
            metadata=ml_service.metadata,
        )
    except Exception as e:
        logger.error(f"Failed to retrieve model info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve model info: {str(e)}",
        )
