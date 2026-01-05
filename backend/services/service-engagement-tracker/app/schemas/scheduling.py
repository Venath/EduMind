"""
Pydantic schemas for study scheduling
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import date, datetime


class SessionDetail(BaseModel):
    """Individual study session details"""
    session_number: int
    duration_minutes: int
    task_type: str
    suggested_time: str


class TaskBreakdown(BaseModel):
    """Task breakdown for a day"""
    assignment_prep_minutes: int
    quiz_interaction_minutes: int
    forum_engagement_minutes: int
    general_study_minutes: int


class DailySchedule(BaseModel):
    """Daily schedule details"""
    date: str
    day_name: str
    is_light_day: bool
    total_minutes: int
    sessions: List[SessionDetail]
    task_breakdown: TaskBreakdown


class StudyScheduleResponse(BaseModel):
    """Complete study schedule response"""
    id: int
    student_id: str
    week_start_date: date
    week_end_date: date
    session_length_minutes: int
    sessions_per_day: int
    total_study_minutes_per_day: int
    load_reduction_factor: float
    is_light_day: bool
    features_used: Optional[Dict] = None
    daily_schedules: List[DailySchedule]
    generation_method: str
    version: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ScheduleGenerationRequest(BaseModel):
    """Request to generate a new schedule"""
    week_start_date: Optional[date] = Field(
        None,
        description="Start date of the week (defaults to next Monday)"
    )


class ScheduleSummary(BaseModel):
    """Summary of schedule configuration"""
    student_id: str
    week_start_date: date
    session_length_minutes: int
    sessions_per_day: int
    total_study_minutes_per_day: int
    load_reduction_applied: bool
    load_reduction_factor: float
    light_days_count: int
    reasoning: Dict[str, str]  # Explanation of why schedule was generated this way

