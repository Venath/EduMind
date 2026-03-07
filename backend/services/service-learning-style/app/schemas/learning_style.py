"""Pydantic schemas for Learning Style Service"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ===========================
# Enums
# ===========================

class LearningStyleEnum(str, Enum):
    VISUAL = "Visual"
    AUDITORY = "Auditory"
    READING = "Reading"
    KINESTHETIC = "Kinesthetic"
    MIXED = "Mixed"


class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class SeverityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class ResourceType(str, Enum):
    VIDEO = "video"
    ARTICLE = "article"
    INTERACTIVE = "interactive"
    PRACTICE = "practice"
    QUIZ = "quiz"
    CHEATSHEET = "cheatsheet"
    TUTORIAL = "tutorial"


class StruggleType(str, Enum):
    QUIZ_FAILURE = "quiz_failure"
    LOW_ENGAGEMENT = "low_engagement"
    TIME_SPENT_HIGH = "time_spent_high"
    REPEATED_ACCESS = "repeated_access"
    HELP_REQUEST = "help_request"
    MULTIPLE_ATTEMPTS = "multiple_attempts"
    CONFUSION_INDICATOR = "confusion_indicator"
    DROP_PATTERN = "drop_pattern"


# ===========================
# Student Learning Profile
# ===========================

class StudentLearningProfileCreate(BaseModel):
    student_id: str = Field(..., max_length=50)
    learning_style: LearningStyleEnum
    style_confidence: float = Field(..., ge=0.0, le=1.0)
    style_probabilities: Dict[str, float] = Field(default_factory=dict)
    preferred_difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    preferred_resource_types: List[str] = Field(default_factory=list)


class StudentLearningProfileUpdate(BaseModel):
    learning_style: Optional[LearningStyleEnum] = None
    style_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    style_probabilities: Optional[Dict[str, float]] = None
    preferred_difficulty: Optional[DifficultyLevel] = None
    preferred_resource_types: Optional[List[str]] = None
    avg_completion_rate: Optional[float] = Field(None, ge=0.0, le=100.0)


class StudentLearningProfileResponse(BaseModel):
    student_id: str
    learning_style: str
    style_confidence: float
    style_probabilities: Dict[str, float]
    preferred_difficulty: str
    preferred_resource_types: List[str]
    avg_completion_rate: float
    total_resources_completed: int
    total_recommendations_received: int
    struggle_topics: List[str]
    struggle_count: int
    days_tracked: int
    last_activity_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LearningStylePrediction(BaseModel):
    student_id: str
    predicted_style: LearningStyleEnum
    confidence: float = Field(..., ge=0.0, le=1.0)
    probabilities: Dict[str, float]
    features_used: int
    model_version: str


# ===========================
# Learning Resources
# ===========================

class LearningResourceCreate(BaseModel):
    resource_type: ResourceType
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    topic: str = Field(..., max_length=100)
    subject: str = Field(..., max_length=50)
    subtopic: Optional[str] = Field(None, max_length=100)
    difficulty_level: DifficultyLevel
    learning_styles: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    content_path: Optional[str] = None
    thumbnail_url: Optional[str] = None
    estimated_duration: Optional[int] = Field(None, description="Duration in minutes")
    tags: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    created_by: Optional[str] = None

    @field_validator('url', 'content_path')
    @classmethod
    def validate_url_or_path(cls, v, info):
        # At least one of url or content_path must be provided
        return v


class LearningResourceUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    learning_styles: Optional[List[str]] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    estimated_duration: Optional[int] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
    effectiveness_rating: Optional[float] = Field(None, ge=0.0, le=5.0)


class LearningResourceResponse(BaseModel):
    resource_id: int
    resource_type: str
    title: str
    description: Optional[str]
    topic: str
    subject: str
    subtopic: Optional[str]
    difficulty_level: str
    learning_styles: List[str]
    url: Optional[str]
    thumbnail_url: Optional[str]
    estimated_duration: Optional[int]
    tags: List[str]
    popularity_score: float
    effectiveness_rating: float
    total_views: int
    total_completions: int
    avg_helpfulness_rating: float
    is_active: bool
    verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LearningResourceList(BaseModel):
    resources: List[LearningResourceResponse]
    total: int
    page: int
    page_size: int


# ===========================
# Student Struggles
# ===========================

class StudentStruggleCreate(BaseModel):
    student_id: str = Field(..., max_length=50)
    topic: str = Field(..., max_length=100)
    concept: Optional[str] = Field(None, max_length=200)
    struggle_type: StruggleType
    severity: SeverityLevel
    confidence_score: float = Field(default=0.85, ge=0.0, le=1.0)
    context: Dict[str, Any] = Field(default_factory=dict)
    detection_method: Optional[str] = None


class StudentStruggleResponse(BaseModel):
    struggle_id: int
    student_id: str
    topic: str
    concept: Optional[str]
    struggle_type: str
    severity: str
    confidence_score: float
    context: Dict[str, Any]
    detected_at: datetime
    detection_method: Optional[str]
    resolved: bool
    resolved_at: Optional[datetime]
    resolution_method: Optional[str]
    recommendations_sent: int

    class Config:
        from_attributes = True


class StudentStruggleList(BaseModel):
    struggles: List[StudentStruggleResponse]
    total: int
    unresolved: int


# ===========================
# Resource Recommendations
# ===========================

class RecommendationRequest(BaseModel):
    student_id: str = Field(..., max_length=50)
    topic: Optional[str] = None
    struggle_id: Optional[int] = None
    max_recommendations: int = Field(default=5, ge=1, le=10)


class ResourceRecommendationCreate(BaseModel):
    student_id: str = Field(..., max_length=50)
    resource_id: int
    struggle_id: Optional[int] = None
    reason: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    score_breakdown: Dict[str, float] = Field(default_factory=dict)
    rank_position: Optional[int] = None
    priority: SeverityLevel = SeverityLevel.MEDIUM


class ResourceRecommendationResponse(BaseModel):
    recommendation_id: int
    student_id: str
    resource_id: int
    resource: Optional[LearningResourceResponse] = None
    struggle_id: Optional[int]
    reason: str
    relevance_score: float
    score_breakdown: Dict[str, float]
    rank_position: Optional[int]
    recommended_at: datetime
    priority: str
    viewed: bool
    viewed_at: Optional[datetime]
    started: bool
    completed: bool
    completed_at: Optional[datetime]
    completion_percentage: float
    time_spent: int
    helpfulness_rating: Optional[int]
    feedback_comment: Optional[str]

    class Config:
        from_attributes = True


class GenerateRecommendationsResponse(BaseModel):
    """Response from POST /recommendations/generate; includes updated total for UI."""
    recommendations: List[ResourceRecommendationResponse]
    total_recommendations: int


class RecommendationList(BaseModel):
    recommendations: List[ResourceRecommendationResponse]
    total: int
    viewed_count: int
    completed_count: int


# ===========================
# Student Behavior Tracking
# ===========================

class StudentBehaviorCreate(BaseModel):
    student_id: str = Field(..., max_length=50)
    tracking_date: datetime
    video_watch_time: int = Field(default=0, ge=0)
    video_completion_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    video_interactions: int = Field(default=0, ge=0)
    text_read_time: int = Field(default=0, ge=0)
    articles_read: int = Field(default=0, ge=0)
    note_taking_count: int = Field(default=0, ge=0)
    audio_playback_time: int = Field(default=0, ge=0)
    podcast_completions: int = Field(default=0, ge=0)
    simulation_time: int = Field(default=0, ge=0)
    interactive_exercises: int = Field(default=0, ge=0)
    hands_on_activities: int = Field(default=0, ge=0)
    forum_posts: int = Field(default=0, ge=0)
    discussion_participation: int = Field(default=0, ge=0)
    peer_interactions: int = Field(default=0, ge=0)
    diagram_views: int = Field(default=0, ge=0)
    image_interactions: int = Field(default=0, ge=0)
    visual_aid_usage: int = Field(default=0, ge=0)
    total_session_time: int = Field(default=0, ge=0)
    login_count: int = Field(default=1, ge=1)


class StudentBehaviorResponse(BaseModel):
    behavior_id: int
    student_id: str
    tracking_date: datetime
    video_watch_time: int
    video_completion_rate: float
    text_read_time: int
    audio_playback_time: int
    simulation_time: int
    total_session_time: int
    login_count: int

    class Config:
        from_attributes = True


# ===========================
# Analytics & Statistics
# ===========================

class StudentAnalytics(BaseModel):
    student_id: str
    learning_style: str
    style_confidence: float
    total_recommendations: int
    viewed_recommendations: int
    completed_recommendations: int
    avg_completion_rate: float
    total_struggles: int
    unresolved_struggles: int
    struggle_topics: List[str]
    most_effective_resource_types: List[Dict[str, Any]]
    engagement_trend: str  # "improving", "declining", "stable"


class ResourceEffectiveness(BaseModel):
    resource_id: int
    title: str
    resource_type: str
    topic: str
    total_recommendations: int
    view_rate: float
    completion_rate: float
    avg_time_spent: int
    avg_helpfulness_rating: float
    effectiveness_score: float


class SystemStats(BaseModel):
    total_students: int
    total_resources: int
    total_recommendations: int
    total_struggles: int
    unresolved_struggles: int
    learning_style_distribution: Dict[str, int]
    most_common_struggle_topics: List[Dict[str, Any]]
    top_resources: List[Dict[str, Any]]
    avg_recommendation_relevance: float
    recommendation_completion_rate: float


# ===========================
# Feedback
# ===========================

class RecommendationFeedback(BaseModel):
    recommendation_id: int
    helpfulness_rating: int = Field(..., ge=1, le=5)
    feedback_comment: Optional[str] = Field(None, max_length=500)


class RecommendationEngagement(BaseModel):
    recommendation_id: int
    viewed: Optional[bool] = None
    started: Optional[bool] = None
    completed: Optional[bool] = None
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    time_spent: Optional[int] = Field(None, ge=0, description="Time in seconds")











