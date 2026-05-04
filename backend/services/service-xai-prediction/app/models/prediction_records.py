"""SQLAlchemy models for XAI prediction persistence."""

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.core.database import Base, TempStudentsBase


class XAIPredictionRecord(Base):
    """Persist generic XAI prediction requests/responses."""

    __tablename__ = "xai_prediction_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), nullable=False, index=True)

    request_payload = Column(JSONB, nullable=False)
    prediction_payload = Column(JSONB, nullable=False)
    explanation_payload = Column(JSONB, nullable=False)
    recommendations = Column(JSONB, nullable=True)
    model_metrics = Column(JSONB, nullable=True)

    predicted_class = Column(String(64), nullable=False, index=True)
    probability = Column(Float, nullable=False)
    risk_level = Column(String(32), nullable=False, index=True)
    model_version = Column(String(64), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class AcademicRiskPredictionRecord(Base):
    """Persist academic risk prediction requests/responses."""

    __tablename__ = "xai_academic_risk_prediction_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), nullable=False, index=True)

    request_payload = Column(JSONB, nullable=False)
    response_payload = Column(JSONB, nullable=False)
    model_metrics = Column(JSONB, nullable=True)

    risk_level = Column(String(32), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    model_version = Column(String(64), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class TemporaryStudentRecord(TempStudentsBase):
    """Persist manual temporary-student submissions separately from connected students."""

    __tablename__ = "temporary_students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), nullable=False, unique=True, index=True)

    avg_grade = Column(Float, nullable=False)
    grade_consistency = Column(Float, nullable=False)
    grade_range = Column(Float, nullable=False)
    num_assessments = Column(Integer, nullable=False)
    assessment_completion_rate = Column(Float, nullable=False)
    studied_credits = Column(Integer, nullable=False)
    num_of_prev_attempts = Column(Integer, nullable=False)
    low_performance = Column(Integer, nullable=False)
    low_engagement = Column(Integer, nullable=False)
    has_previous_attempts = Column(Integer, nullable=False)

    request_payload = Column(JSONB, nullable=False)
    response_payload = Column(JSONB, nullable=True)

    latest_risk_level = Column(String(32), nullable=True, index=True)
    latest_risk_score = Column(Float, nullable=True)
    latest_confidence = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        index=True,
    )


class TemporaryStudentPredictionRecord(TempStudentsBase):
    """Persist every temporary-student prediction so timeline history is available."""

    __tablename__ = "temporary_student_prediction_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), nullable=False, index=True)

    request_payload = Column(JSONB, nullable=False)
    response_payload = Column(JSONB, nullable=False)

    risk_level = Column(String(32), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
