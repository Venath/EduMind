"""
Academic Risk Prediction Routes
"""

from app.core.logging import get_logger
from app.schemas.academic_risk import AcademicRiskRequest, AcademicRiskResponse
from app.Services.academic_risk_service import academic_risk_service
from fastapi import APIRouter, HTTPException, status

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/academic-risk/predict",
    response_model=AcademicRiskResponse,
    status_code=status.HTTP_200_OK,
)
async def predict_academic_risk(request: AcademicRiskRequest):
    """
    Predict student academic dropout risk using OULAD model

    Args:
        request: Student academic performance features

    Returns:
        Risk prediction with personalized recommendations
    """
    try:
        logger.info(
            f"Academic risk prediction request for student: {request.student_id}"
        )

        # Make prediction
        response = await academic_risk_service.predict(request)

        logger.info(
            f"Prediction complete: {response.risk_level} "
            f"(confidence: {response.confidence:.2%}, risk_score: {response.risk_score:.2%})"
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


@router.get("/academic-risk/model-info")
async def get_academic_risk_model_info():
    """Get information about the OULAD academic risk model"""
    try:
        return {
            "model_type": academic_risk_service.metadata["model_type"],
            "features": academic_risk_service.feature_names,
            "classes": academic_risk_service.metadata["classes"],
            "accuracy": academic_risk_service.metadata["accuracy"],
            "description": "Binary classification model for predicting student dropout risk based on academic performance",
        }
    except Exception as e:
        logger.error(f"Failed to retrieve model info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve model info: {str(e)}",
        )
