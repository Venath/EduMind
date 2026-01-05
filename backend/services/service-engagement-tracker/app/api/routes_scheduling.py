"""
Study Scheduling API Routes

Personalized study schedules based on engagement features
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.api.dependencies import get_db
from app.models import StudySchedule
from app.schemas.scheduling import (
    StudyScheduleResponse,
    ScheduleGenerationRequest,
    ScheduleSummary
)
from app.services.scheduling_service import SchedulingService

router = APIRouter(prefix="/api/v1/schedules", tags=["Study Scheduling"])


@router.post("/students/{student_id}/generate", response_model=StudyScheduleResponse)
def generate_schedule(
    student_id: str,
    request: ScheduleGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a personalized study schedule for a student
    
    **Features Used:**
    - Session length personalization (session_score, volatility, consecutive_low_days)
    - Time-of-day scheduling (engagement_score_lag_1day, rolling_avg_7days, is_declining)
    - Course effort rebalancing (assignment_score, interaction_score, forum_score)
    - Decline-aware load reduction (is_declining, engagement_score_lag_7days, rolling_avg_30days)
    
    **Schedule Output:**
    - Personalized session length (15-90 minutes)
    - Number of sessions per day (1-5)
    - Daily task breakdown (assignments, quizzes, forum, general study)
    - Light day predictions (reduced workload on predicted low-engagement days)
    
    **Example:**
    - Student A: 20-min × 3 blocks/day (high volatility, low session score)
    - Student B: 45-min × 1 block/day (low volatility, high session score)
    """
    try:
        service = SchedulingService(db)
        schedule = service.generate_weekly_schedule(
            student_id=student_id,
            week_start_date=request.week_start_date
        )
        saved_schedule = service.save_schedule(schedule)
        return saved_schedule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating schedule: {str(e)}")


@router.get("/students/{student_id}")
def get_student_schedule(
    student_id: str,
    week_start_date: Optional[date] = Query(None, description="Week start date (defaults to current week)"),
    db: Session = Depends(get_db)
):
    """
    Get existing schedule for a student
    
    Returns 200 with null if no schedule exists (to prevent browser console errors).
    Use POST /generate to create a new schedule.
    """
    try:
        service = SchedulingService(db)
        schedule = service.get_student_schedule(student_id, week_start_date)
        
        if not schedule:
            # Return 200 with null instead of 404 to prevent browser console errors
            return {"schedule": None, "message": f"No schedule found for student {student_id}"}
        
        return schedule
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving schedule: {str(e)}"
        )


@router.get("/students/{student_id}/summary", response_model=ScheduleSummary)
def get_schedule_summary(
    student_id: str,
    week_start_date: Optional[date] = Query(None, description="Week start date"),
    db: Session = Depends(get_db)
):
    """
    Get a summary of the schedule with reasoning
    
    Returns a simplified view explaining:
    - Why the schedule was configured this way
    - Which features influenced the decisions
    - Load reduction reasoning
    """
    try:
        service = SchedulingService(db)
        schedule = service.get_student_schedule(student_id, week_start_date)
        
        if not schedule:
            raise HTTPException(
                status_code=404,
                detail=f"No schedule found for student {student_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving schedule summary: {str(e)}"
        )
    
    # Extract reasoning from features
    features = schedule.features_used or {}
    reasoning = {}
    
    # Session length reasoning
    if features.get('engagement_volatility_7days', 0) > 20:
        reasoning['session_length'] = (
            f"Short sessions ({schedule.session_length_minutes} min) due to high engagement volatility "
            f"({features.get('engagement_volatility_7days', 0):.1f}). Student needs frequent, manageable blocks."
        )
    elif features.get('session_score', 0) > 70:
        reasoning['session_length'] = (
            f"Longer sessions ({schedule.session_length_minutes} min) because student has high session score "
            f"({features.get('session_score', 0):.1f}) and can maintain focus."
        )
    else:
        reasoning['session_length'] = (
            f"Standard session length ({schedule.session_length_minutes} min) based on session score "
            f"({features.get('session_score', 0):.1f})."
        )
    
    # Sessions per day reasoning
    reasoning['sessions_per_day'] = (
        f"{schedule.sessions_per_day} sessions per day to achieve {schedule.total_study_minutes_per_day} "
        f"minutes of daily study time."
    )
    
    # Load reduction reasoning
    if schedule.load_reduction_factor < 1.0:
        reduction_pct = int((1.0 - schedule.load_reduction_factor) * 100)
        reasoning['load_reduction'] = (
            f"{reduction_pct}% load reduction applied due to declining engagement trend. "
            f"This prevents burnout while maintaining learning momentum."
        )
    else:
        reasoning['load_reduction'] = "No load reduction needed. Student engagement is stable or improving."
    
    # Light days reasoning
    # daily_schedules is stored as JSONB, so it's already a list of dicts
    if isinstance(schedule.daily_schedules, list):
        light_days = sum(1 for day in schedule.daily_schedules if day.get('is_light_day', False))
    else:
        light_days = 0
    if light_days > 0:
        reasoning['light_days'] = (
            f"{light_days} light day(s) predicted based on engagement patterns. "
            f"These days have reduced workload to prevent overload."
        )
    else:
        reasoning['light_days'] = "No light days predicted. Student can handle full workload."
    
    # Course effort rebalancing reasoning
    if features.get('assignment_score', 0) < 40 and features.get('login_score', 0) > 50:
        reasoning['task_distribution'] = (
            "Assignment prep scheduled early in week (Mon-Wed) to address avoidance behavior. "
            "Student logs in but avoids assignments, so we front-load assignment work."
        )
    else:
        reasoning['task_distribution'] = "Standard task distribution across the week."
    
    return ScheduleSummary(
        student_id=student_id,
        week_start_date=schedule.week_start_date,
        session_length_minutes=schedule.session_length_minutes,
        sessions_per_day=schedule.sessions_per_day,
        total_study_minutes_per_day=schedule.total_study_minutes_per_day,
        load_reduction_applied=schedule.load_reduction_factor < 1.0,
        load_reduction_factor=schedule.load_reduction_factor,
        light_days_count=light_days,
        reasoning=reasoning
    )


@router.delete("/students/{student_id}")
def delete_schedule(
    student_id: str,
    week_start_date: Optional[date] = Query(None, description="Week start date"),
    db: Session = Depends(get_db)
):
    """
    Delete a schedule for a student
    """
    service = SchedulingService(db)
    schedule = service.get_student_schedule(student_id, week_start_date)
    
    if not schedule:
        raise HTTPException(
            status_code=404,
            detail=f"No schedule found for student {student_id}"
        )
    
    db.delete(schedule)
    db.commit()
    
    return {"message": "Schedule deleted successfully"}


@router.get("/students/{student_id}/features")
def get_scheduling_features(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the engagement features that would be used for scheduling
    
    Useful for understanding what data influences schedule generation
    """
    try:
        service = SchedulingService(db)
        features = service.get_engagement_features(student_id)
        return {
            "student_id": student_id,
            "features": features,
            "explanations": {
                "session_score": "Current session engagement score (0-100). Higher = can handle longer sessions.",
                "engagement_volatility_7days": "Standard deviation of engagement scores over 7 days. Higher = more unpredictable, needs shorter sessions.",
                "consecutive_low_days": "Number of consecutive days with engagement < 40. Higher = burnout risk, needs shorter sessions.",
                "engagement_score_lag_1day": "Previous day's engagement score. Used to predict tomorrow's engagement.",
                "rolling_avg_7days": "7-day moving average of engagement. Used for trend detection.",
                "rolling_avg_30days": "30-day moving average. Used to detect temporary vs. long-term decline.",
                "is_declining": "Whether engagement trend is declining. Triggers load reduction.",
                "assignment_score": "Assignment completion score. Low + high login = avoidance behavior.",
                "interaction_score": "Content interaction score. Low = needs more interactive tasks.",
                "forum_score": "Forum participation score. Low = needs more social engagement."
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

