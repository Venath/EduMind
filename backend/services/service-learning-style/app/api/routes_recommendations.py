"""API routes for recommendations"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.dependencies import get_db
from app.schemas import (
    RecommendationRequest,
    ResourceRecommendationResponse,
    RecommendationList,
    RecommendationFeedback,
    RecommendationEngagement,
    GenerateRecommendationsResponse,
)
from app.models import ResourceRecommendation, LearningResource, StudentLearningProfile
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/generate", response_model=GenerateRecommendationsResponse)
def generate_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """Generate personalized resource recommendations for a student. Returns list and updated system total so UI can refresh the Recommendations count."""
    student = db.query(StudentLearningProfile).filter(
        StudentLearningProfile.student_id == request.student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {request.student_id} not found"
        )

    service = RecommendationService(db)
    scored_resources = service.generate_recommendations(
        student_id=request.student_id,
        topic=request.topic,
        struggle_id=request.struggle_id,
        max_recommendations=request.max_recommendations
    )

    recommendations = service.save_recommendations(
        student_id=request.student_id,
        scored_resources=scored_resources,
        struggle_id=request.struggle_id
    )

    for rec in recommendations:
        rec.resource = db.query(LearningResource).filter(
            LearningResource.resource_id == rec.resource_id
        ).first()

    total_recommendations = db.query(func.count(ResourceRecommendation.recommendation_id)).scalar() or 0
    return GenerateRecommendationsResponse(
        recommendations=recommendations,
        total_recommendations=total_recommendations,
    )


@router.get("/student/{student_id}", response_model=RecommendationList)
def get_student_recommendations(
    student_id: str,
    viewed_only: bool = False,
    completed_only: bool = False,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get all recommendations for a student"""
    query = db.query(ResourceRecommendation).filter(
        ResourceRecommendation.student_id == student_id
    )
    
    if viewed_only:
        query = query.filter(ResourceRecommendation.viewed == True)
    
    if completed_only:
        query = query.filter(ResourceRecommendation.completed == True)
    
    recommendations = query.order_by(
        ResourceRecommendation.recommended_at.desc()
    ).limit(limit).all()
    
    # Load resource data
    for rec in recommendations:
        rec.resource = db.query(LearningResource).filter(
            LearningResource.resource_id == rec.resource_id
        ).first()
    
    # Calculate stats
    total = len(recommendations)
    viewed_count = sum(1 for r in recommendations if r.viewed)
    completed_count = sum(1 for r in recommendations if r.completed)
    
    return RecommendationList(
        recommendations=recommendations,
        total=total,
        viewed_count=viewed_count,
        completed_count=completed_count
    )


@router.get("/{recommendation_id}", response_model=ResourceRecommendationResponse)
def get_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific recommendation by ID"""
    recommendation = db.query(ResourceRecommendation).filter(
        ResourceRecommendation.recommendation_id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation {recommendation_id} not found"
        )
    
    # Load resource data
    recommendation.resource = db.query(LearningResource).filter(
        LearningResource.resource_id == recommendation.resource_id
    ).first()
    
    return recommendation


@router.post("/{recommendation_id}/engagement")
def update_recommendation_engagement(
    recommendation_id: int,
    engagement: RecommendationEngagement,
    db: Session = Depends(get_db)
):
    """Update engagement tracking for a recommendation"""
    recommendation = db.query(ResourceRecommendation).filter(
        ResourceRecommendation.recommendation_id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation {recommendation_id} not found"
        )
    
    from datetime import datetime
    
    # Update fields
    if engagement.viewed is not None:
        recommendation.viewed = engagement.viewed
        if engagement.viewed and not recommendation.viewed_at:
            recommendation.viewed_at = datetime.now()
    
    if engagement.started is not None:
        recommendation.started = engagement.started
        if engagement.started and not recommendation.started_at:
            recommendation.started_at = datetime.now()
    
    if engagement.completed is not None:
        recommendation.completed = engagement.completed
        if engagement.completed and not recommendation.completed_at:
            recommendation.completed_at = datetime.now()
    
    if engagement.completion_percentage is not None:
        recommendation.completion_percentage = engagement.completion_percentage
    
    if engagement.time_spent is not None:
        recommendation.time_spent = engagement.time_spent
    
    db.commit()
    
    return {"message": "Engagement updated successfully"}


@router.post("/{recommendation_id}/feedback")
def submit_recommendation_feedback(
    recommendation_id: int,
    feedback: RecommendationFeedback,
    db: Session = Depends(get_db)
):
    """Submit feedback for a recommendation"""
    recommendation = db.query(ResourceRecommendation).filter(
        ResourceRecommendation.recommendation_id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation {recommendation_id} not found"
        )
    
    from datetime import datetime
    
    recommendation.helpfulness_rating = feedback.helpfulness_rating
    recommendation.feedback_comment = feedback.feedback_comment
    recommendation.feedback_at = datetime.now()
    
    db.commit()
    
    return {"message": "Feedback submitted successfully"}











