"""
Student Analytics API Routes
Comprehensive student analytics combining engagement scores and predictions
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import date, timedelta

from app.api.dependencies import get_db
from app.models import EngagementScore, DisengagementPrediction, DailyEngagementMetric
from app.schemas import StudentAnalytics, EngagementSummary, EngagementScoreResponse, DisengagementPredictionResponse

router = APIRouter(prefix="/api/v1/students", tags=["Student Analytics"])


@router.get("/{student_id}/analytics", response_model=StudentAnalytics)
def get_student_analytics(
    student_id: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics for a student
    
    Includes:
    - Engagement summary
    - Latest score
    - Latest prediction
    - Historical engagement scores
    - Historical predictions
    """
    # Get engagement scores
    cutoff_date = date.today() - timedelta(days=days)
    
    engagement_scores = db.query(EngagementScore).filter(
        EngagementScore.student_id == student_id,
        EngagementScore.date >= cutoff_date
    ).order_by(EngagementScore.date).all()
    
    if not engagement_scores:
        raise HTTPException(status_code=404, detail=f"No data found for student {student_id}")
    
    # Calculate summary
    avg_score = sum(s.engagement_score for s in engagement_scores) / len(engagement_scores)
    latest_score = max(engagement_scores, key=lambda s: s.date)
    
    engagement_summary = EngagementSummary(
        student_id=student_id,
        days_tracked=len(engagement_scores),
        avg_engagement_score=round(avg_score, 2),
        current_engagement_level=latest_score.engagement_level,
        trend=latest_score.engagement_trend,
        last_updated=latest_score.date
    )
    
    # Get predictions
    predictions = db.query(DisengagementPrediction).filter(
        DisengagementPrediction.student_id == student_id,
        DisengagementPrediction.prediction_date >= cutoff_date
    ).order_by(DisengagementPrediction.prediction_date).all()
    
    latest_prediction = max(predictions, key=lambda p: p.prediction_date) if predictions else None
    
    # Get date range
    min_date = min(s.date for s in engagement_scores)
    max_date = max(s.date for s in engagement_scores)
    
    return StudentAnalytics(
        student_id=student_id,
        date_range={"start": min_date, "end": max_date},
        engagement_summary=engagement_summary,
        latest_score=latest_score,
        latest_prediction=latest_prediction,
        engagement_history=engagement_scores,
        risk_history=predictions
    )


@router.get("/{student_id}/dashboard")
def get_student_dashboard(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    Get dashboard data for a student (simplified view)
    """
    # Latest engagement score
    latest_score = db.query(EngagementScore).filter(
        EngagementScore.student_id == student_id
    ).order_by(desc(EngagementScore.date)).first()
    
    if not latest_score:
        raise HTTPException(status_code=404, detail=f"No data found for student {student_id}")
    
    # Latest prediction
    latest_prediction = db.query(DisengagementPrediction).filter(
        DisengagementPrediction.student_id == student_id
    ).order_by(desc(DisengagementPrediction.prediction_date)).first()
    
    # Last 7 days engagement (relative to latest data, not today)
    seven_days_ago = latest_score.date - timedelta(days=7)
    recent_scores = db.query(EngagementScore).filter(
        EngagementScore.student_id == student_id,
        EngagementScore.date >= seven_days_ago,
        EngagementScore.date <= latest_score.date
    ).order_by(EngagementScore.date).all()
    
    # Calculate 7-day trend
    if len(recent_scores) >= 2:
        first_score = recent_scores[0].engagement_score
        last_score = recent_scores[-1].engagement_score
        trend_direction = "improving" if last_score > first_score else "declining" if last_score < first_score else "stable"
        trend_change = round(last_score - first_score, 2)
    else:
        trend_direction = "insufficient_data"
        trend_change = 0.0
    
    return {
        "student_id": student_id,
        "current_status": {
            "engagement_score": round(latest_score.engagement_score, 2),
            "engagement_level": latest_score.engagement_level,
            "at_risk": latest_prediction.at_risk if latest_prediction else False,
            "risk_level": latest_prediction.risk_level if latest_prediction else "Unknown",
            "risk_probability": round(latest_prediction.risk_probability, 3) if latest_prediction else None
        },
        "recent_trend": {
            "direction": trend_direction,
            "change": trend_change,
            "days_analyzed": len(recent_scores)
        },
        "component_scores": {
            "login": round(latest_score.login_score, 2),
            "session": round(latest_score.session_score, 2),
            "interaction": round(latest_score.interaction_score, 2),
            "forum": round(latest_score.forum_score, 2),
            "assignment": round(latest_score.assignment_score, 2)
        },
        "alerts": generate_alerts(latest_score, latest_prediction),
        "last_updated": latest_score.date.isoformat()
    }


def generate_alerts(score: EngagementScore, prediction: Optional[DisengagementPrediction]) -> List[dict]:
    """Generate actionable alerts based on student data"""
    alerts = []
    
    # High risk alert
    if prediction and prediction.risk_level == "High":
        alerts.append({
            "severity": "high",
            "message": "Student is at HIGH risk of disengagement",
            "action": "Immediate intervention recommended"
        })
    
    # Low engagement alert
    if score.engagement_score < 40:
        alerts.append({
            "severity": "warning",
            "message": "Low engagement detected",
            "action": "Monitor student progress closely"
        })
    
    # Declining trend alert
    if score.engagement_trend == "Declining":
        alerts.append({
            "severity": "warning",
            "message": "Engagement trend is declining",
            "action": "Consider proactive outreach"
        })
    
    # Component-specific alerts
    if score.session_score < 30:
        alerts.append({
            "severity": "info",
            "message": "Low session activity detected",
            "action": "Encourage more time on platform"
        })
    
    if score.forum_score < 20:
        alerts.append({
            "severity": "info",
            "message": "Limited forum participation",
            "action": "Encourage peer interaction"
        })
    
    if not alerts:
        alerts.append({
            "severity": "success",
            "message": "Student engagement is healthy",
            "action": "Continue monitoring"
        })
    
    return alerts


@router.get("/list")
def list_students(
    engagement_level: Optional[str] = Query(None, description="Filter by engagement level"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all students with basic info and filters
    """
    # Get latest scores for all students
    subquery = db.query(
        EngagementScore.student_id,
        func.max(EngagementScore.date).label('latest_date')
    ).group_by(EngagementScore.student_id).subquery()
    
    # Join to get full score data
    query = db.query(EngagementScore).join(
        subquery,
        (EngagementScore.student_id == subquery.c.student_id) &
        (EngagementScore.date == subquery.c.latest_date)
    )
    
    # Apply filters
    if engagement_level:
        query = query.filter(EngagementScore.engagement_level == engagement_level)
    
    scores = query.offset(offset).limit(limit).all()
    
    # Build response with predictions
    students = []
    for score in scores:
        # Get latest prediction
        prediction = db.query(DisengagementPrediction).filter(
            DisengagementPrediction.student_id == score.student_id
        ).order_by(desc(DisengagementPrediction.prediction_date)).first()
        
        # Filter by risk level if specified
        if risk_level and (not prediction or prediction.risk_level != risk_level):
            continue
        
        students.append({
            "student_id": score.student_id,
            "engagement_score": round(score.engagement_score, 2),
            "engagement_level": score.engagement_level,
            "engagement_trend": score.engagement_trend,
            "at_risk": prediction.at_risk if prediction else False,
            "risk_level": prediction.risk_level if prediction else "Unknown",
            "risk_probability": round(prediction.risk_probability, 3) if prediction else None,
            "last_updated": score.date.isoformat()
        })
    
    return {
        "total": len(students),
        "offset": offset,
        "limit": limit,
        "students": students
    }


@router.get("/compare")
def compare_students(
    student_ids: str = Query(..., description="Comma-separated student IDs"),
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Compare multiple students side-by-side
    """
    ids = [id.strip() for id in student_ids.split(',')]
    
    if len(ids) < 2 or len(ids) > 10:
        raise HTTPException(status_code=400, detail="Please provide 2-10 student IDs")
    
    cutoff_date = date.today() - timedelta(days=days)
    
    comparison = []
    for student_id in ids:
        # Get scores
        scores = db.query(EngagementScore).filter(
            EngagementScore.student_id == student_id,
            EngagementScore.date >= cutoff_date
        ).all()
        
        if not scores:
            comparison.append({
                "student_id": student_id,
                "error": "No data found"
            })
            continue
        
        # Calculate metrics
        avg_score = sum(s.engagement_score for s in scores) / len(scores)
        latest = max(scores, key=lambda s: s.date)
        
        # Get prediction
        prediction = db.query(DisengagementPrediction).filter(
            DisengagementPrediction.student_id == student_id
        ).order_by(desc(DisengagementPrediction.prediction_date)).first()
        
        comparison.append({
            "student_id": student_id,
            "avg_engagement_score": round(avg_score, 2),
            "current_engagement_score": round(latest.engagement_score, 2),
            "engagement_level": latest.engagement_level,
            "trend": latest.engagement_trend,
            "at_risk": prediction.at_risk if prediction else False,
            "risk_probability": round(prediction.risk_probability, 3) if prediction else None,
            "days_analyzed": len(scores)
        })
    
    return {
        "comparison": comparison,
        "analysis_period_days": days
    }

