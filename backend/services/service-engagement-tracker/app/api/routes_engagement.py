"""
Engagement Score API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.api.dependencies import get_db
from app.models import EngagementScore, DailyEngagementMetric
from app.schemas import (
    EngagementScoreResponse,
    EngagementSummary,
    DailyMetricResponse
)

router = APIRouter(prefix="/api/v1/engagement", tags=["Engagement Scores"])


@router.get("/students/{student_id}/latest", response_model=EngagementScoreResponse)
def get_latest_engagement_score(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the latest engagement score for a student
    """
    score = db.query(EngagementScore).filter(
        EngagementScore.student_id == student_id
    ).order_by(desc(EngagementScore.date)).first()
    
    if not score:
        raise HTTPException(status_code=404, detail=f"No engagement data found for student {student_id}")
    
    return score


@router.get("/students/{student_id}/history", response_model=List[EngagementScoreResponse])
def get_engagement_history(
    student_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Get engagement score history for a student
    """
    scores = db.query(EngagementScore).filter(
        EngagementScore.student_id == student_id
    ).order_by(desc(EngagementScore.date)).limit(days).all()
    
    if not scores:
        raise HTTPException(status_code=404, detail=f"No engagement history found for student {student_id}")
    
    # Return in chronological order
    return list(reversed(scores))


@router.get("/students/{student_id}/summary", response_model=EngagementSummary)
def get_engagement_summary(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    Get engagement summary for a student
    """
    # Get all scores for student
    scores = db.query(EngagementScore).filter(
        EngagementScore.student_id == student_id
    ).all()
    
    if not scores:
        raise HTTPException(status_code=404, detail=f"No engagement data found for student {student_id}")
    
    # Calculate summary
    avg_score = sum(s.engagement_score for s in scores) / len(scores)
    latest = max(scores, key=lambda s: s.date)
    
    return EngagementSummary(
        student_id=student_id,
        days_tracked=len(scores),
        avg_engagement_score=round(avg_score, 2),
        current_engagement_level=latest.engagement_level,
        trend=latest.engagement_trend,
        last_updated=latest.date
    )


@router.get("/students/{student_id}/date/{target_date}", response_model=EngagementScoreResponse)
def get_engagement_by_date(
    student_id: str,
    target_date: date,
    db: Session = Depends(get_db)
):
    """
    Get engagement score for a specific date
    """
    score = db.query(EngagementScore).filter(
        EngagementScore.student_id == student_id,
        EngagementScore.date == target_date
    ).first()
    
    if not score:
        raise HTTPException(
            status_code=404,
            detail=f"No engagement data found for student {student_id} on {target_date}"
        )
    
    return score


@router.get("/students/{student_id}/metrics", response_model=List[DailyMetricResponse])
def get_daily_metrics(
    student_id: str,
    days: int = Query(7, ge=1, le=90, description="Number of days to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Get raw daily engagement metrics for a student
    """
    metrics = db.query(DailyEngagementMetric).filter(
        DailyEngagementMetric.student_id == student_id
    ).order_by(desc(DailyEngagementMetric.date)).limit(days).all()
    
    if not metrics:
        raise HTTPException(status_code=404, detail=f"No daily metrics found for student {student_id}")
    
    return list(reversed(metrics))


@router.get("/leaderboard", response_model=List[EngagementSummary])
def get_engagement_leaderboard(
    limit: int = Query(10, ge=1, le=100, description="Number of students to return"),
    db: Session = Depends(get_db)
):
    """
    Get top engaged students (leaderboard)
    """
    # Get average engagement per student
    subquery = db.query(
        EngagementScore.student_id,
        func.avg(EngagementScore.engagement_score).label('avg_score'),
        func.count(EngagementScore.id).label('days_tracked'),
        func.max(EngagementScore.date).label('last_date')
    ).group_by(EngagementScore.student_id).subquery()
    
    # Get top students
    top_students = db.query(subquery).order_by(desc('avg_score')).limit(limit).all()
    
    # Build response
    leaderboard = []
    for student in top_students:
        latest_score = db.query(EngagementScore).filter(
            EngagementScore.student_id == student.student_id,
            EngagementScore.date == student.last_date
        ).first()
        
        leaderboard.append(EngagementSummary(
            student_id=student.student_id,
            days_tracked=student.days_tracked,
            avg_engagement_score=round(student.avg_score, 2),
            current_engagement_level=latest_score.engagement_level if latest_score else "Medium",
            trend=latest_score.engagement_trend if latest_score else None,
            last_updated=student.last_date
        ))
    
    return leaderboard


@router.get("/low-engagement", response_model=List[EngagementSummary])
def get_low_engagement_students(
    threshold: float = Query(40.0, ge=0, le=100, description="Engagement score threshold"),
    days: int = Query(7, ge=1, le=30, description="Number of recent days to check"),
    db: Session = Depends(get_db)
):
    """
    Get students with consistently low engagement
    """
    # Get students with low average engagement in recent days
    cutoff_date = date.today() - timedelta(days=days)
    
    subquery = db.query(
        EngagementScore.student_id,
        func.avg(EngagementScore.engagement_score).label('avg_score'),
        func.count(EngagementScore.id).label('days_tracked'),
        func.max(EngagementScore.date).label('last_date')
    ).filter(
        EngagementScore.date >= cutoff_date,
        EngagementScore.engagement_score < threshold
    ).group_by(EngagementScore.student_id).subquery()
    
    low_students = db.query(subquery).order_by('avg_score').all()
    
    # Build response
    result = []
    for student in low_students:
        latest_score = db.query(EngagementScore).filter(
            EngagementScore.student_id == student.student_id,
            EngagementScore.date == student.last_date
        ).first()
        
        result.append(EngagementSummary(
            student_id=student.student_id,
            days_tracked=student.days_tracked,
            avg_engagement_score=round(student.avg_score, 2),
            current_engagement_level=latest_score.engagement_level if latest_score else "Low",
            trend=latest_score.engagement_trend if latest_score else None,
            last_updated=student.last_date
        ))
    
    return result


@router.get("/trends/declining", response_model=List[EngagementSummary])
def get_declining_students(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get students with declining engagement trends
    """
    # Get recent scores with declining trend
    recent_declining = db.query(EngagementScore).filter(
        EngagementScore.engagement_trend == 'Declining',
        EngagementScore.date >= date.today() - timedelta(days=7)
    ).all()
    
    # Group by student and count declining days
    from collections import defaultdict
    student_declining_days = defaultdict(int)
    student_latest = {}
    
    for score in recent_declining:
        student_declining_days[score.student_id] += 1
        if score.student_id not in student_latest or score.date > student_latest[score.student_id].date:
            student_latest[score.student_id] = score
    
    # Sort by number of declining days
    sorted_students = sorted(
        student_declining_days.items(),
        key=lambda x: x[1],
        reverse=True
    )[:limit]
    
    result = []
    for student_id, declining_days in sorted_students:
        latest = student_latest[student_id]
        
        # Get average score
        avg_score = db.query(func.avg(EngagementScore.engagement_score)).filter(
            EngagementScore.student_id == student_id
        ).scalar()
        
        result.append(EngagementSummary(
            student_id=student_id,
            days_tracked=declining_days,
            avg_engagement_score=round(avg_score, 2),
            current_engagement_level=latest.engagement_level,
            trend="Declining",
            last_updated=latest.date
        ))
    
    return result

