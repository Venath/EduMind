# Import all schemas here
from app.schemas.engagement import (
    EventCreate,
    DateRangeQuery,
    EngagementScoreResponse,
    EngagementSummary,
    DisengagementPredictionResponse,
    AtRiskStudent,
    DailyMetricResponse,
    StudentAnalytics,
    BatchPredictionRequest,
    BatchPredictionResponse,
    HealthResponse,
    StatsResponse,
    ErrorResponse,
    EngagementLevel,
    RiskLevel,
    TrendType,
    EventType
)
from app.schemas.scheduling import (
    StudyScheduleResponse,
    ScheduleGenerationRequest,
    ScheduleSummary,
    DailySchedule,
    SessionDetail,
    TaskBreakdown
)

__all__ = [
    "EventCreate",
    "DateRangeQuery",
    "EngagementScoreResponse",
    "EngagementSummary",
    "DisengagementPredictionResponse",
    "AtRiskStudent",
    "DailyMetricResponse",
    "StudentAnalytics",
    "BatchPredictionRequest",
    "BatchPredictionResponse",
    "HealthResponse",
    "StatsResponse",
    "ErrorResponse",
    "EngagementLevel",
    "RiskLevel",
    "TrendType",
    "EventType",
    "StudyScheduleResponse",
    "ScheduleGenerationRequest",
    "ScheduleSummary",
    "DailySchedule",
    "SessionDetail",
    "TaskBreakdown"
]

