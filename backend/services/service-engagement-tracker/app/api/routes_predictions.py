"""
Disengagement Prediction API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.api.dependencies import get_db
from app.models import DisengagementPrediction, EngagementScore
from app.schemas import (
    DisengagementPredictionResponse,
    AtRiskStudent,
    BatchPredictionRequest,
    BatchPredictionResponse
)

router = APIRouter(prefix="/api/v1/predictions", tags=["Disengagement Predictions"])


@router.get("/students/{student_id}/latest", response_model=DisengagementPredictionResponse)
def get_latest_prediction(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the latest disengagement prediction for a student
    """
    prediction = db.query(DisengagementPrediction).filter(
        DisengagementPrediction.student_id == student_id
    ).order_by(desc(DisengagementPrediction.prediction_date)).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail=f"No predictions found for student {student_id}")
    
    return prediction


@router.get("/students/{student_id}/history", response_model=List[DisengagementPredictionResponse])
def get_prediction_history(
    student_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Get prediction history for a student
    """
    predictions = db.query(DisengagementPrediction).filter(
        DisengagementPrediction.student_id == student_id
    ).order_by(desc(DisengagementPrediction.prediction_date)).limit(days).all()
    
    if not predictions:
        raise HTTPException(status_code=404, detail=f"No prediction history found for student {student_id}")
    
    return list(reversed(predictions))


@router.get("/at-risk", response_model=List[AtRiskStudent])
def get_at_risk_students(
    risk_level: Optional[str] = Query(None, description="Filter by risk level (High/Medium/Low)"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get list of at-risk students with their latest predictions
    """
    # Base query
    query = db.query(DisengagementPrediction).filter(
        DisengagementPrediction.at_risk == True
    )
    
    # Filter by risk level if specified
    if risk_level:
        query = query.filter(DisengagementPrediction.risk_level == risk_level)
    
    # Get recent predictions (last 7 days)
    recent_date = date.today() - timedelta(days=7)
    query = query.filter(DisengagementPrediction.prediction_date >= recent_date)
    
    predictions = query.all()
    
    # Group by student and aggregate
    from collections import defaultdict
    student_data = defaultdict(lambda: {
        'risk_probs': [],
        'engagement_scores': [],
        'dates': [],
        'high_risk_days': 0,
        'factors': set()
    })
    
    for pred in predictions:
        student_data[pred.student_id]['risk_probs'].append(pred.risk_probability)
        student_data[pred.student_id]['dates'].append(pred.prediction_date)
        if pred.risk_level == 'High':
            student_data[pred.student_id]['high_risk_days'] += 1
        
        # Collect contributing factors
        if pred.contributing_factors:
            for factor, value in pred.contributing_factors.items():
                if value:
                    student_data[pred.student_id]['factors'].add(factor)
        
        # Get corresponding engagement score
        eng_score = db.query(EngagementScore).filter(
            EngagementScore.student_id == pred.student_id,
            EngagementScore.date == pred.prediction_date
        ).first()
        
        if eng_score:
            student_data[pred.student_id]['engagement_scores'].append(eng_score.engagement_score)
    
    # Build response
    result = []
    for student_id, data in student_data.items():
        if data['risk_probs']:
            result.append(AtRiskStudent(
                student_id=student_id,
                avg_risk_probability=round(sum(data['risk_probs']) / len(data['risk_probs']), 3),
                latest_engagement_score=round(data['engagement_scores'][-1], 2) if data['engagement_scores'] else 0.0,
                days_at_high_risk=data['high_risk_days'],
                last_prediction_date=max(data['dates']),
                contributing_factors=list(data['factors'])
            ))
    
    # Sort by risk probability
    result.sort(key=lambda x: x.avg_risk_probability, reverse=True)
    
    return result[:limit]


@router.get("/high-risk", response_model=List[AtRiskStudent])
def get_high_risk_students(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get students with HIGH risk level
    """
    return get_at_risk_students(risk_level="High", limit=limit, db=db)


@router.get("/students/{student_id}/risk-trajectory")
def get_risk_trajectory(
    student_id: str,
    days: int = Query(14, ge=7, le=90),
    db: Session = Depends(get_db)
):
    """
    Get risk probability trajectory over time for a student
    """
    cutoff_date = date.today() - timedelta(days=days)
    
    predictions = db.query(DisengagementPrediction).filter(
        DisengagementPrediction.student_id == student_id,
        DisengagementPrediction.prediction_date >= cutoff_date
    ).order_by(DisengagementPrediction.prediction_date).all()
    
    if not predictions:
        raise HTTPException(status_code=404, detail=f"No recent predictions for student {student_id}")
    
    # Build trajectory data
    trajectory = []
    for pred in predictions:
        trajectory.append({
            "date": pred.prediction_date.isoformat(),
            "risk_probability": round(pred.risk_probability, 3),
            "risk_level": pred.risk_level,
            "at_risk": pred.at_risk
        })
    
    # Calculate trend
    if len(trajectory) >= 2:
        first_risk = trajectory[0]['risk_probability']
        last_risk = trajectory[-1]['risk_probability']
        change = last_risk - first_risk
        trend = "improving" if change < -0.05 else "worsening" if change > 0.05 else "stable"
    else:
        trend = "insufficient_data"
    
    return {
        "student_id": student_id,
        "days_analyzed": len(trajectory),
        "trend": trend,
        "current_risk": trajectory[-1] if trajectory else None,
        "trajectory": trajectory
    }


@router.get("/statistics")
def get_prediction_statistics(db: Session = Depends(get_db)):
    """
    Get overall prediction statistics
    """
    # Get most recent predictions (last 7 days)
    recent_date = date.today() - timedelta(days=7)
    recent_predictions = db.query(DisengagementPrediction).filter(
        DisengagementPrediction.prediction_date >= recent_date
    ).all()
    
    if not recent_predictions:
        raise HTTPException(status_code=404, detail="No recent predictions found")
    
    # Calculate statistics
    total = len(recent_predictions)
    at_risk_count = sum(1 for p in recent_predictions if p.at_risk)
    high_risk = sum(1 for p in recent_predictions if p.risk_level == 'High')
    medium_risk = sum(1 for p in recent_predictions if p.risk_level == 'Medium')
    low_risk = sum(1 for p in recent_predictions if p.risk_level == 'Low')
    
    avg_risk_prob = sum(p.risk_probability for p in recent_predictions) / total if total > 0 else 0
    
    # Unique students
    unique_students = len(set(p.student_id for p in recent_predictions))
    unique_at_risk = len(set(p.student_id for p in recent_predictions if p.at_risk))
    
    return {
        "total_predictions": total,
        "unique_students": unique_students,
        "at_risk_predictions": at_risk_count,
        "at_risk_students": unique_at_risk,
        "at_risk_percentage": round((at_risk_count / total) * 100, 2) if total > 0 else 0,
        "risk_levels": {
            "high": high_risk,
            "medium": medium_risk,
            "low": low_risk
        },
        "average_risk_probability": round(avg_risk_prob, 3),
        "analysis_period_days": 7,
        "latest_prediction_date": max(p.prediction_date for p in recent_predictions).isoformat()
    }


@router.post("/generate", response_model=BatchPredictionResponse)
def generate_predictions(
    request: BatchPredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Trigger batch prediction generation
    
    NOTE: This is a placeholder. In production, this would trigger
    an async job (Celery task) to run the ML model.
    """
    start_time = datetime.now()
    
    # For now, just return existing predictions
    # In production, this would trigger: python scripts/train_disengagement_model.py
    
    query = db.query(DisengagementPrediction)
    
    # Filter by student IDs if provided
    if request.student_ids:
        query = query.filter(DisengagementPrediction.student_id.in_(request.student_ids))
    
    # Filter by date if provided
    if request.prediction_date:
        query = query.filter(DisengagementPrediction.prediction_date == request.prediction_date)
    else:
        # Get most recent predictions
        latest_date = db.query(func.max(DisengagementPrediction.prediction_date)).scalar()
        if latest_date:
            query = query.filter(DisengagementPrediction.prediction_date == latest_date)
    
    predictions = query.all()
    
    # Count by risk level
    high_risk = sum(1 for p in predictions if p.risk_level == 'High')
    medium_risk = sum(1 for p in predictions if p.risk_level == 'Medium')
    low_risk = sum(1 for p in predictions if p.risk_level == 'Low')
    
    processing_time = (datetime.now() - start_time).total_seconds()
    
    return BatchPredictionResponse(
        total_predictions=len(predictions),
        high_risk_count=high_risk,
        medium_risk_count=medium_risk,
        low_risk_count=low_risk,
        processing_time_seconds=round(processing_time, 2),
        predictions=predictions[:100]  # Limit response size
    )


@router.get("/model-info")
def get_model_info(db: Session = Depends(get_db)):
    """
    Get information about the prediction model
    """
    # Get latest prediction to extract model info
    latest = db.query(DisengagementPrediction).order_by(
        desc(DisengagementPrediction.created_at)
    ).first()
    
    if not latest:
        raise HTTPException(status_code=404, detail="No predictions found")
    
    return {
        "model_version": latest.model_version,
        "model_type": latest.model_type,
        "prediction_horizon_days": latest.prediction_horizon_days,
        "last_trained": latest.created_at.isoformat(),
        "feature_importance": latest.feature_importance[:10] if latest.feature_importance else [],
        "threshold_config": {
            "at_risk_threshold": 30,  # Engagement score < 30
            "high_risk_probability": 0.7,
            "medium_risk_probability": 0.4
        }
    }

