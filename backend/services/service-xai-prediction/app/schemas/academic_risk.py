"""
Academic Risk Prediction Schemas for OULAD Model
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class AcademicRiskRequest(BaseModel):
    """Request schema for academic risk prediction"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "student_id": "student_12345",
                "avg_grade": 65.5,
                "grade_consistency": 85.2,
                "grade_range": 30.0,
                "num_assessments": 8,
                "assessment_completion_rate": 0.8,
                "studied_credits": 60,
                "num_of_prev_attempts": 0,
                "low_performance": 0,
                "low_engagement": 0,
                "has_previous_attempts": 0,
            }
        }
    )

    student_id: str
    avg_grade: float = Field(
        ..., ge=0, le=100, description="Average assessment score (0-100)"
    )
    grade_consistency: float = Field(
        ..., ge=0, le=100, description="Performance consistency score"
    )
    grade_range: float = Field(
        ..., ge=0, le=100, description="Score variability (max - min)"
    )
    num_assessments: int = Field(
        ..., ge=0, description="Number of assessments completed"
    )
    assessment_completion_rate: float = Field(
        ..., ge=0, le=1, description="Completion rate (0-1)"
    )
    studied_credits: int = Field(..., ge=0, description="Course credits enrolled")
    num_of_prev_attempts: int = Field(
        ..., ge=0, description="Number of previous attempts"
    )
    low_performance: int = Field(..., ge=0, le=1, description="Binary: grade < 40%")
    low_engagement: int = Field(
        ..., ge=0, le=1, description="Binary: low assessment completion"
    )
    has_previous_attempts: int = Field(
        ..., ge=0, le=1, description="Binary: has failed before"
    )


class AcademicRiskResponse(BaseModel):
    """Response schema for academic risk prediction"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "student_id": "student_12345",
                "risk_level": "At-Risk",
                "risk_score": 0.847,
                "confidence": 0.847,
                "probabilities": {"Safe": 0.153, "At-Risk": 0.847},
                "recommendations": [
                    "Seek immediate tutoring - grade is critically low",
                    "Complete all remaining assessments",
                    "Contact academic advisor immediately",
                ],
                "top_risk_factors": [
                    {"feature": "avg_grade", "value": 35.5, "impact": "high"},
                    {"feature": "num_assessments", "value": 3, "impact": "high"},
                ],
                "prediction_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-15T10:30:00",
            }
        }
    )

    student_id: str
    risk_level: str = Field(..., description="Safe or At-Risk")
    risk_score: float = Field(
        ..., ge=0, le=1, description="Probability of being at-risk"
    )
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")
    probabilities: dict = Field(..., description="Probabilities for each class")
    recommendations: List[str] = Field(..., description="Personalized recommendations")
    top_risk_factors: List[dict] = Field(
        ..., description="Top factors contributing to risk"
    )
    counterfactual: Optional["CounterfactualExplanation"] = Field(
        default=None,
        description="Minimal feature changes that could move the student into a safer outcome",
    )
    prediction_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CounterfactualChange(BaseModel):
    """One recommended feature adjustment for reaching a safer outcome."""

    feature: str
    current_value: str | float | int | bool
    suggested_value: str | float | int | bool
    direction: str = Field(..., description="increase, decrease, toggle, or maintain")
    delta: Optional[float] = Field(
        default=None,
        description="Signed numeric change where applicable",
    )
    rationale: str


class CounterfactualExplanation(BaseModel):
    """Counterfactual path from the current outcome to a safer one."""

    current_outcome: str
    target_outcome: str
    achievable: bool
    summary: str
    estimated_risk_level: Optional[str] = None
    estimated_risk_score: Optional[float] = Field(default=None, ge=0, le=1)
    estimated_confidence: Optional[float] = Field(default=None, ge=0, le=1)
    changes: List[CounterfactualChange] = Field(default_factory=list)


class TemporaryStudentSummary(BaseModel):
    """Summary view for saved temporary-student records."""

    student_id: str
    avg_grade: float
    latest_risk_level: Optional[str] = None
    latest_risk_score: Optional[float] = None
    latest_confidence: Optional[float] = None
    updated_at: Optional[datetime] = None


class TemporaryStudentListResponse(BaseModel):
    """Paginated list of saved temporary-student records."""

    query: str
    total: int
    limit: int
    students: List[TemporaryStudentSummary]


class TemporaryStudentRecordResponse(BaseModel):
    """Detailed saved temporary-student record with prediction payload."""

    student_id: str
    request_payload: AcademicRiskRequest
    prediction: Optional[AcademicRiskResponse] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RiskTimelinePoint(BaseModel):
    """One persisted XAI prediction point for timeline rendering."""

    timestamp: datetime
    risk_level: str
    risk_score: float = Field(..., ge=0, le=1)
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    avg_grade: Optional[float] = Field(default=None, ge=0, le=100)
    completion_rate: Optional[float] = Field(default=None, ge=0, le=100)
    key_driver: Optional[str] = None


class RiskTimelineResponse(BaseModel):
    """Timeline of persisted XAI predictions for one student."""

    student_id: str
    total_points: int
    trend_direction: str
    timeline_basis: str = Field(
        default="saved_history",
        description="derived_history, saved_history, temporary_history, temporary_snapshot, or current_analysis",
    )
    latest_risk_level: Optional[str] = None
    latest_risk_score: Optional[float] = Field(default=None, ge=0, le=1)
    points: List[RiskTimelinePoint] = Field(default_factory=list)


class SimilarStudentCase(BaseModel):
    """One comparable student drawn from the connected or temporary cohort."""

    student_id: str
    similarity_score: float = Field(..., ge=0, le=1)
    risk_level: str
    risk_score: float = Field(..., ge=0, le=1)
    avg_grade: float = Field(..., ge=0, le=100)
    completion_rate: float = Field(..., ge=0, le=100)
    learning_style: Optional[str] = None
    engagement_level: Optional[str] = None
    explanation: str


class RankedIntervention(BaseModel):
    """One ranked intervention with simulated impact on the current student."""

    title: str
    rank: int = Field(..., ge=1)
    effort: str
    confidence: float = Field(..., ge=0, le=1)
    expected_risk_reduction: float = Field(..., ge=0, le=1)
    expected_new_risk_level: str
    expected_new_risk_score: float = Field(..., ge=0, le=1)
    rationale: str
    evidence: List[str] = Field(default_factory=list)


class CohortMetricComparison(BaseModel):
    """Comparison of one student metric against the cohort."""

    label: str
    student_value: float
    cohort_average: float
    percentile: float = Field(..., ge=0, le=100)
    direction: str


class CohortComparison(BaseModel):
    """Student position relative to the broader connected or temporary cohort."""

    cohort_size: int = Field(..., ge=0)
    summary: str
    average_risk_score: Optional[float] = Field(default=None, ge=0, le=1)
    average_avg_grade: Optional[float] = Field(default=None, ge=0, le=100)
    average_completion_rate: Optional[float] = Field(default=None, ge=0, le=100)
    risk_percentile: Optional[float] = Field(default=None, ge=0, le=100)
    performance_percentile: Optional[float] = Field(default=None, ge=0, le=100)
    completion_percentile: Optional[float] = Field(default=None, ge=0, le=100)
    metrics: List[CohortMetricComparison] = Field(default_factory=list)


class FairnessAlert(BaseModel):
    """One fairness or bias warning derived from subgroup disparities."""

    severity: str
    title: str
    detail: str


class FairnessDimensionCheck(BaseModel):
    """Fairness parity check for the current student's subgroup within one dimension."""

    dimension: str
    current_group: str
    group_size: int = Field(..., ge=0)
    average_risk_score: float = Field(..., ge=0, le=1)
    cohort_average_risk_score: float = Field(..., ge=0, le=1)
    disparity_score: float = Field(..., ge=-1, le=1)
    elevated_risk_rate: float = Field(..., ge=0, le=100)
    status: str
    note: str


class FairnessEvaluation(BaseModel):
    """Fairness and bias diagnostics across integrated student subgroups."""

    parity_score: float = Field(..., ge=0, le=100)
    summary: str
    overall_average_risk_score: float = Field(..., ge=0, le=1)
    overall_elevated_risk_rate: float = Field(..., ge=0, le=100)
    dimensions: List[FairnessDimensionCheck] = Field(default_factory=list)
    alerts: List[FairnessAlert] = Field(default_factory=list)


class StabilityFeatureSignal(BaseModel):
    """Sensitivity signal for one feature under local perturbations."""

    feature: str
    tested_range: str
    max_risk_shift: float = Field(..., ge=0, le=100)
    outcome_changed: bool
    sensitivity: str


class ExplanationStabilityEvaluation(BaseModel):
    """Robustness summary for the current prediction and explanation."""

    stability_score: float = Field(..., ge=0, le=100)
    consistency_rate: float = Field(..., ge=0, le=100)
    average_risk_shift: float = Field(..., ge=0, le=100)
    confidence_band: str
    summary: str
    sensitive_features: List[StabilityFeatureSignal] = Field(default_factory=list)


class CaseOutcomeExplorerEntry(BaseModel):
    """Outcome-oriented view of one comparable historical case."""

    student_id: str
    similarity_score: float = Field(..., ge=0, le=100)
    trajectory: str
    observed_outcome: str
    latest_risk_level: str
    latest_risk_score: float = Field(..., ge=0, le=1)
    learning_style: Optional[str] = None
    recommended_action: Optional[str] = None
    key_takeaway: str


class CaseOutcomeExplorer(BaseModel):
    """Outcome explorer built from the strongest comparable student cases."""

    summary: str
    cases: List[CaseOutcomeExplorerEntry] = Field(default_factory=list)


class StudentInsightsRequest(BaseModel):
    """Payload for generating integrated XAI insights from the current prediction."""

    source: str = Field(..., description="connected or temporary")
    institute_id: Optional[str] = None
    request_payload: AcademicRiskRequest
    prediction: AcademicRiskResponse


class StudentInsightsResponse(BaseModel):
    """Combined insight payload for similar cases, interventions, and cohort context."""

    student_id: str
    source: str
    similar_cases: List[SimilarStudentCase] = Field(default_factory=list)
    interventions: List[RankedIntervention] = Field(default_factory=list)
    cohort_comparison: Optional[CohortComparison] = None
    fairness_evaluation: Optional[FairnessEvaluation] = None
    explanation_stability: Optional[ExplanationStabilityEvaluation] = None
    case_outcome_explorer: Optional[CaseOutcomeExplorer] = None


AcademicRiskResponse.model_rebuild()
