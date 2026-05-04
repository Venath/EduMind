"""
Test API endpoints for the XAI Prediction Service.
"""

from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import academic_risk_routes
from app.api.dependencies import get_db, get_temp_students_db
from app.schemas.academic_risk import (
    AcademicRiskRequest,
    AcademicRiskResponse,
    CaseOutcomeExplorer,
    CaseOutcomeExplorerEntry,
    CohortComparison,
    CohortMetricComparison,
    ExplanationStabilityEvaluation,
    FairnessAlert,
    FairnessDimensionCheck,
    FairnessEvaluation,
    RankedIntervention,
    RiskTimelinePoint,
    RiskTimelineResponse,
    SimilarStudentCase,
    StabilityFeatureSignal,
    StudentInsightsResponse,
)
from app.schemas.prediction import PredictionRequest
from app.services.student_insights_service import student_insights_service
from app.services.student_insights_service import InsightCandidate
from app.services.sync_service import sync_service
from app.services.sync_service import SyncServiceError


@pytest.fixture
def client():
    """Create a test client using context manager for proper cleanup."""
    with TestClient(app) as test_client:
        yield test_client


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check(self, client):
        """Test that health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_contains_service_name(self, client):
        """Test that health response contains service name."""
        response = client.get("/health")
        data = response.json()
        assert "service" in data


class TestPredictionEndpoint:
    """Tests for the prediction endpoint."""

    def test_predict_endpoint_exists(self, client):
        """Test that predict endpoint exists."""
        response = client.post(
            "/api/v1/predict",
            json={
                "student_id": "test_student",
                "total_interactions": 100,
                "days_active": 30,
                "avg_score": 75.0,
                "submissions_on_time": 8,
                "total_submissions": 10,
                "forum_posts": 5,
                "time_spent_hours": 50.0,
                "resources_accessed": 20,
                "quiz_attempts": 5,
                "assignment_completion_rate": 0.8,
            },
        )
        assert response.status_code in [200, 201, 422]

    def test_predict_with_valid_data(self, client):
        """Test prediction with valid input data."""
        response = client.post(
            "/api/v1/predict",
            json={
                "student_id": "student_123",
                "total_interactions": 150,
                "avg_response_time": 45.5,
                "consistency_score": 0.75,
                "days_inactive": 3,
                "completion_rate": 0.65,
                "assessment_score": 72.5,
            },
        )
        if response.status_code == 200:
            data = response.json()
            assert "prediction" in data
            assert "risk_level" in data["prediction"]
            assert "probability" in data["prediction"]


class TestAcademicRiskEndpoint:
    """Tests for the academic risk endpoint."""

    def test_academic_risk_endpoint_exists(self, client):
        """Test that academic risk endpoint exists."""
        response = client.post(
            "/api/v1/academic-risk/predict",
            json={
                "student_id": "test_student",
                "total_clicks": 100,
                "days_active": 30,
                "avg_score": 75.0,
                "studied_credits": 60,
                "num_of_prev_attempts": 1,
            },
        )
        assert response.status_code in [200, 201, 422]

    def test_temporary_student_prediction_endpoint(self, client, monkeypatch):
        """Manual temporary-student submissions should use the separate endpoint."""

        async def fake_predict(request: AcademicRiskRequest):
            return AcademicRiskResponse(
                student_id=request.student_id,
                risk_level="Medium Risk",
                risk_score=0.52,
                confidence=0.81,
                probabilities={
                    "Safe": 0.18,
                    "Medium Risk": 0.52,
                    "At-Risk": 0.30,
                },
                recommendations=["Follow up with a tutor"],
                top_risk_factors=[
                    {"feature": "avg_grade", "value": request.avg_grade, "impact": "high"}
                ],
                prediction_id="123e4567-e89b-12d3-a456-426614174000",
                timestamp="2026-03-08T10:30:00",
            )

        def fake_persist_temporary_student_record(db, request, response):
            return None

        monkeypatch.setattr(academic_risk_routes.academic_risk_service, "predict", fake_predict)
        monkeypatch.setattr(
            academic_risk_routes,
            "persist_temporary_student_record",
            fake_persist_temporary_student_record,
        )

        response = client.post(
            "/api/v1/academic-risk/temporary-students/predict",
            json={
                "student_id": "temp_student_001",
                "avg_grade": 70,
                "grade_consistency": 85,
                "grade_range": 30,
                "num_assessments": 8,
                "assessment_completion_rate": 0.8,
                "studied_credits": 60,
                "num_of_prev_attempts": 0,
                "low_performance": 0,
                "low_engagement": 0,
                "has_previous_attempts": 0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == "temp_student_001"
        assert data["risk_level"] == "Medium Risk"

    def test_academic_risk_stats_endpoint(self, client):
        """Stats endpoint should surface average performance from XAI records."""

        class FakeQuery:
            def __init__(self, items):
                self.items = items

            def order_by(self, *_args, **_kwargs):
                return self

            def all(self):
                return self.items

        class FakeSession:
            def __init__(self, items):
                self.items = items

            def query(self, *_args, **_kwargs):
                return FakeQuery(self.items)

        connected_records = [
            SimpleNamespace(
                student_id="STU0001",
                created_at=datetime(2026, 3, 8, 12, 0, 0),
                request_payload={"avg_grade": 80},
                risk_score=0.2,
                risk_level="Safe",
            ),
            SimpleNamespace(
                student_id="STU0001",
                created_at=datetime(2026, 3, 7, 12, 0, 0),
                request_payload={"avg_grade": 60},
                risk_score=0.5,
                risk_level="At-Risk",
            ),
            SimpleNamespace(
                student_id="STU0002",
                created_at=datetime(2026, 3, 8, 12, 0, 0),
                request_payload={"avg_grade": 70},
                risk_score=0.7,
                risk_level="At-Risk",
            ),
        ]

        temp_records = [
            SimpleNamespace(
                student_id="TEMP001",
                avg_grade=55,
                latest_risk_level="At-Risk",
            )
        ]

        app.dependency_overrides[get_db] = lambda: FakeSession(connected_records)
        app.dependency_overrides[get_temp_students_db] = lambda: FakeSession(temp_records)

        try:
            response = client.get("/api/v1/academic-risk/stats")
        finally:
            app.dependency_overrides.pop(get_db, None)
            app.dependency_overrides.pop(get_temp_students_db, None)

        assert response.status_code == 200
        data = response.json()
        assert data["total_students_analyzed"] == 2
        assert data["average_performance"] == 75.0
        assert data["high_risk_students"] == 1

    def test_list_temporary_students_endpoint(self, client):
        """Saved temporary students should be listable for the manual XAI flow."""

        class FakeQuery:
            def __init__(self, items):
                self.items = items

            def order_by(self, *_args, **_kwargs):
                return self

            def filter(self, *_args, **_kwargs):
                return self

            def limit(self, value):
                self.items = self.items[:value]
                return self

            def all(self):
                return self.items

        class FakeSession:
            def __init__(self, items):
                self.items = items

            def query(self, *_args, **_kwargs):
                return FakeQuery(self.items)

        temp_records = [
            SimpleNamespace(
                student_id="TEMP001",
                avg_grade=72.0,
                latest_risk_level="Medium Risk",
                latest_risk_score=0.55,
                latest_confidence=0.81,
                updated_at=datetime(2026, 3, 9, 12, 0, 0),
                created_at=datetime(2026, 3, 9, 10, 0, 0),
            ),
            SimpleNamespace(
                student_id="TEMP002",
                avg_grade=48.0,
                latest_risk_level="At-Risk",
                latest_risk_score=0.82,
                latest_confidence=0.88,
                updated_at=datetime(2026, 3, 9, 11, 0, 0),
                created_at=datetime(2026, 3, 9, 9, 0, 0),
            ),
        ]

        app.dependency_overrides[get_temp_students_db] = lambda: FakeSession(temp_records)

        try:
            response = client.get("/api/v1/academic-risk/temporary-students?limit=5")
        finally:
            app.dependency_overrides.pop(get_temp_students_db, None)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["students"][0]["student_id"] == "TEMP001"
        assert data["students"][0]["latest_risk_level"] == "Medium Risk"

    def test_student_risk_timeline_endpoint(self, client, monkeypatch):
        """Timeline endpoint should return persisted XAI history in chronological order."""

        class FakeQuery:
            def __init__(self, items):
                self.items = items

            def filter(self, *_args, **_kwargs):
                return self

            def order_by(self, *_args, **_kwargs):
                return self

            def limit(self, value):
                self.items = self.items[:value]
                return self

            def all(self):
                return self.items

            def first(self):
                return self.items[0] if self.items else None

        class FakeSession:
            def __init__(self, model_items):
                self.model_items = model_items

            def query(self, model):
                return FakeQuery(self.model_items.get(model, []))

        academic_records = [
            SimpleNamespace(
                student_id="STU0003",
                created_at=datetime(2026, 3, 9, 12, 0, 0),
                request_payload={
                    "avg_grade": 58,
                    "assessment_completion_rate": 0.68,
                    "grade_consistency": 72,
                },
                risk_score=0.44,
                risk_level="Medium Risk",
                confidence=0.83,
            ),
            SimpleNamespace(
                student_id="STU0003",
                created_at=datetime(2026, 3, 8, 12, 0, 0),
                request_payload={
                    "avg_grade": 48,
                    "assessment_completion_rate": 0.51,
                    "grade_consistency": 61,
                },
                risk_score=0.76,
                risk_level="At-Risk",
                confidence=0.88,
            ),
        ]

        app.dependency_overrides[get_db] = lambda: FakeSession(
            {academic_risk_routes.AcademicRiskPredictionRecord: academic_records}
        )
        app.dependency_overrides[get_temp_students_db] = lambda: FakeSession(
            {academic_risk_routes.TemporaryStudentRecord: []}
        )

        async def fake_build_connected_timeline(student_id: str, limit: int = 8, days: int = 30):
            return RiskTimelineResponse(
                student_id=student_id,
                total_points=2,
                trend_direction="improving",
                timeline_basis="derived_history",
                latest_risk_level="Medium Risk",
                latest_risk_score=0.44,
                points=[
                    RiskTimelinePoint(
                        timestamp=datetime(2026, 3, 8, 12, 0, 0),
                        risk_level="At-Risk",
                        risk_score=0.76,
                        confidence=0.88,
                        avg_grade=48.0,
                        completion_rate=51.0,
                        key_driver="Baseline XAI analysis recorded.",
                    ),
                    RiskTimelinePoint(
                        timestamp=datetime(2026, 3, 9, 12, 0, 0),
                        risk_level="Medium Risk",
                        risk_score=0.44,
                        confidence=0.83,
                        avg_grade=58.0,
                        completion_rate=68.0,
                        key_driver="Largest shift came from Average grade improving across the saved timeline.",
                    ),
                ],
            )

        monkeypatch.setattr(
            sync_service,
            "build_connected_timeline",
            fake_build_connected_timeline,
        )

        try:
            response = client.get("/api/v1/academic-risk/students/STU0003/timeline?limit=5")
        finally:
            app.dependency_overrides.pop(get_db, None)
            app.dependency_overrides.pop(get_temp_students_db, None)

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == "STU0003"
        assert data["total_points"] == 2
        assert data["timeline_basis"] == "derived_history"
        assert data["trend_direction"] == "improving"
        assert data["points"][0]["risk_level"] == "At-Risk"
        assert data["points"][1]["risk_level"] == "Medium Risk"
        assert "Largest shift" in data["points"][1]["key_driver"]

    def test_connected_timeline_derives_from_history_when_no_saved_records(
        self, client, monkeypatch
    ):
        """Connected timeline should be derived from engagement history before returning 404."""

        class FakeQuery:
            def __init__(self, items):
                self.items = items

            def filter(self, *_args, **_kwargs):
                return self

            def order_by(self, *_args, **_kwargs):
                return self

            def limit(self, value):
                self.items = self.items[:value]
                return self

            def all(self):
                return self.items

            def first(self):
                return self.items[0] if self.items else None

        class FakeSession:
            def __init__(self, model_items):
                self.model_items = model_items

            def query(self, model):
                return FakeQuery(self.model_items.get(model, []))

        async def fake_build_connected_timeline(student_id: str, limit: int, days: int):
            assert student_id == "STU0007"
            assert limit == 5
            assert days >= 20
            return RiskTimelineResponse(
                student_id=student_id,
                total_points=2,
                trend_direction="improving",
                latest_risk_level="Medium Risk",
                latest_risk_score=0.44,
                points=[
                    RiskTimelinePoint(
                        timestamp=datetime(2026, 3, 8, 12, 0, 0),
                        risk_level="At-Risk",
                        risk_score=0.72,
                        confidence=0.81,
                        avg_grade=48.0,
                        completion_rate=51.0,
                        key_driver="Baseline connected-student analysis derived from engagement history.",
                    ),
                    RiskTimelinePoint(
                        timestamp=datetime(2026, 3, 9, 12, 0, 0),
                        risk_level="Medium Risk",
                        risk_score=0.44,
                        confidence=0.86,
                        avg_grade=58.0,
                        completion_rate=68.0,
                        key_driver="Largest shift: Completion rate changed by +17.0%.",
                    ),
                ],
            )

        app.dependency_overrides[get_db] = lambda: FakeSession(
            {academic_risk_routes.AcademicRiskPredictionRecord: []}
        )
        app.dependency_overrides[get_temp_students_db] = lambda: FakeSession(
            {
                academic_risk_routes.TemporaryStudentPredictionRecord: [],
                academic_risk_routes.TemporaryStudentRecord: [],
            }
        )
        monkeypatch.setattr(
            sync_service,
            "build_connected_timeline",
            fake_build_connected_timeline,
        )

        try:
            response = client.get("/api/v1/academic-risk/students/STU0007/timeline?limit=5&source=connected")
        finally:
            app.dependency_overrides.pop(get_db, None)
            app.dependency_overrides.pop(get_temp_students_db, None)

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == "STU0007"
        assert data["total_points"] == 2
        assert data["points"][0]["risk_level"] == "At-Risk"
        assert data["points"][1]["risk_level"] == "Medium Risk"

    def test_temporary_student_risk_timeline_endpoint(self, client):
        """Temporary students should also return a real saved timeline when history exists."""

        class FakeQuery:
            def __init__(self, items):
                self.items = items

            def filter(self, *_args, **_kwargs):
                return self

            def order_by(self, *_args, **_kwargs):
                return self

            def limit(self, value):
                self.items = self.items[:value]
                return self

            def all(self):
                return self.items

            def first(self):
                return self.items[0] if self.items else None

        class FakeSession:
            def __init__(self, model_items):
                self.model_items = model_items

            def query(self, model):
                return FakeQuery(self.model_items.get(model, []))

        temp_history = [
            SimpleNamespace(
                student_id="TEMP001",
                created_at=datetime(2026, 3, 9, 12, 0, 0),
                request_payload={
                    "avg_grade": 62,
                    "assessment_completion_rate": 0.71,
                    "grade_consistency": 77,
                },
                risk_score=0.41,
                risk_level="Medium Risk",
                confidence=0.82,
            ),
            SimpleNamespace(
                student_id="TEMP001",
                created_at=datetime(2026, 3, 8, 12, 0, 0),
                request_payload={
                    "avg_grade": 49,
                    "assessment_completion_rate": 0.56,
                    "grade_consistency": 64,
                },
                risk_score=0.79,
                risk_level="At-Risk",
                confidence=0.87,
            ),
        ]

        app.dependency_overrides[get_db] = lambda: FakeSession(
            {academic_risk_routes.AcademicRiskPredictionRecord: []}
        )
        app.dependency_overrides[get_temp_students_db] = lambda: FakeSession(
            {
                academic_risk_routes.TemporaryStudentPredictionRecord: temp_history,
                academic_risk_routes.TemporaryStudentRecord: [],
            }
        )

        try:
            response = client.get(
                "/api/v1/academic-risk/students/TEMP001/timeline?limit=5&source=temporary"
            )
        finally:
            app.dependency_overrides.pop(get_db, None)
            app.dependency_overrides.pop(get_temp_students_db, None)

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == "TEMP001"
        assert data["total_points"] == 2
        assert data["trend_direction"] == "improving"
        assert data["points"][0]["risk_level"] == "At-Risk"
        assert data["points"][1]["risk_level"] == "Medium Risk"

    def test_get_temporary_student_record_endpoint(self, client):
        """A saved temporary student should return its form payload and prediction."""

        class FakeQuery:
            def __init__(self, items):
                self.items = items

            def filter(self, *_args, **_kwargs):
                return self

            def order_by(self, *_args, **_kwargs):
                return self

            def first(self):
                return self.items[0] if self.items else None

        class FakeSession:
            def __init__(self, items):
                self.items = items

            def query(self, *_args, **_kwargs):
                return FakeQuery(self.items)

        temp_record = SimpleNamespace(
            student_id="TEMP001",
            request_payload={
                "student_id": "TEMP001",
                "avg_grade": 72,
                "grade_consistency": 85,
                "grade_range": 20,
                "num_assessments": 8,
                "assessment_completion_rate": 0.75,
                "studied_credits": 60,
                "num_of_prev_attempts": 0,
                "low_performance": 0,
                "low_engagement": 0,
                "has_previous_attempts": 0,
            },
            response_payload={
                "student_id": "TEMP001",
                "risk_level": "Medium Risk",
                "risk_score": 0.61,
                "confidence": 0.84,
                "probabilities": {
                    "Safe": 0.16,
                    "Medium Risk": 0.61,
                    "At-Risk": 0.23,
                },
                "recommendations": ["Follow up with the student"],
                "top_risk_factors": [
                    {"feature": "avg_grade", "value": 72, "impact": "medium"}
                ],
                "prediction_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2026-03-09T12:00:00",
            },
            created_at=datetime(2026, 3, 9, 10, 0, 0),
            updated_at=datetime(2026, 3, 9, 12, 0, 0),
        )

        app.dependency_overrides[get_temp_students_db] = lambda: FakeSession([temp_record])

        try:
            response = client.get("/api/v1/academic-risk/temporary-students/TEMP001")
        finally:
            app.dependency_overrides.pop(get_temp_students_db, None)

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == "TEMP001"
        assert data["request_payload"]["avg_grade"] == 72
        assert data["prediction"]["risk_level"] == "Medium Risk"


class TestConnectedAcademicRiskEndpoints:
    """Tests for connected student search and request-building endpoints."""

    def test_search_students_endpoint(self, client, monkeypatch):
        async def fake_search_students(
            query: str = "",
            limit: int = 10,
            institute_id: str = "LMS_INST_A",
        ):
            return {
                "query": query,
                "total": 1,
                "limit": limit,
                "institute_id": institute_id,
                "students": [
                    {
                        "student_id": "STU0001",
                        "engagement_score": 72.5,
                        "engagement_level": "High",
                        "engagement_trend": "Improving",
                        "risk_level": "Low",
                        "risk_probability": 0.12,
                        "learning_style": "Visual",
                        "avg_completion_rate": 81.0,
                        "has_learning_profile": True,
                        "last_updated": "2026-03-08",
                    }
                ],
            }

        monkeypatch.setattr(sync_service, "search_students", fake_search_students)

        response = client.get(
            "/api/v1/academic-risk/students/search",
            params={"query": "STU", "limit": 5},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["students"][0]["student_id"] == "STU0001"
        assert data["students"][0]["has_learning_profile"] is True

    def test_connected_student_request_endpoint(self, client, monkeypatch):
        async def fake_build_academic_risk_request(
            student_id: str,
            days: int = 14,
        ):
            return AcademicRiskRequest(
                student_id=student_id,
                avg_grade=68.0,
                grade_consistency=84.0,
                grade_range=16.0,
                num_assessments=6,
                assessment_completion_rate=0.75,
                studied_credits=60,
                num_of_prev_attempts=0,
                low_performance=0,
                low_engagement=0,
                has_previous_attempts=0,
            )

        monkeypatch.setattr(
            sync_service,
            "build_academic_risk_request",
            fake_build_academic_risk_request,
        )

        response = client.get("/api/v1/academic-risk/students/STU0001/request")

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == "STU0001"
        assert data["avg_grade"] == 68.0

    def test_search_students_falls_back_to_local_history(self, client, monkeypatch):
        async def fake_search_students(
            query: str = "",
            limit: int = 10,
            institute_id: str = "LMS_INST_A",
        ):
            raise SyncServiceError(status_code=502, detail="engagement unavailable")

        def fake_local_search(db, query: str, limit: int, institute_id: str):
            return {
                "query": query,
                "total": 1,
                "limit": limit,
                "institute_id": institute_id,
                "students": [
                    {
                        "student_id": "Stu01",
                        "engagement_score": 0.0,
                        "engagement_level": "Unavailable",
                        "engagement_trend": None,
                        "risk_level": "At-Risk",
                        "risk_probability": 0.91,
                        "learning_style": None,
                        "avg_completion_rate": 80.0,
                        "has_learning_profile": False,
                        "last_updated": "2026-03-08T10:00:00",
                    }
                ],
            }

        monkeypatch.setattr(sync_service, "search_students", fake_search_students)
        monkeypatch.setattr(
            academic_risk_routes,
            "search_local_prediction_history",
            fake_local_search,
        )

        response = client.get(
            "/api/v1/academic-risk/students/search",
            params={"query": "Stu", "limit": 5},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["students"][0]["student_id"] == "Stu01"
        assert data["students"][0]["engagement_level"] == "Unavailable"

    def test_connected_student_request_falls_back_to_local_request(self, client, monkeypatch):
        async def fake_build_academic_risk_request(
            student_id: str,
            days: int = 14,
        ):
            raise SyncServiceError(status_code=502, detail="engagement unavailable")

        def fake_local_request(db, student_id: str):
            return AcademicRiskRequest(
                student_id=student_id,
                avg_grade=55.0,
                grade_consistency=70.0,
                grade_range=20.0,
                num_assessments=5,
                assessment_completion_rate=0.6,
                studied_credits=60,
                num_of_prev_attempts=1,
                low_performance=0,
                low_engagement=1,
                has_previous_attempts=1,
            )

        monkeypatch.setattr(
            sync_service,
            "build_academic_risk_request",
            fake_build_academic_risk_request,
        )
        monkeypatch.setattr(
            academic_risk_routes,
            "get_local_prediction_request",
            fake_local_request,
        )

        response = client.get("/api/v1/academic-risk/students/Stu01/request")

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == "Stu01"
        assert data["low_engagement"] == 1

    def test_student_insights_endpoint(self, client, monkeypatch):
        async def sample_build_insights(payload, db, temp_db):
            return StudentInsightsResponse(
                student_id=payload.request_payload.student_id,
                source=payload.source,
                similar_cases=[
                    SimilarStudentCase(
                        student_id="STU0008",
                        similarity_score=0.87,
                        risk_level="Medium Risk",
                        risk_score=0.61,
                        avg_grade=58.0,
                        completion_rate=72.0,
                        learning_style="Visual",
                        engagement_level="Medium",
                        explanation="Closest match due to similar average grade band.",
                    )
                ],
                interventions=[
                    RankedIntervention(
                        title="Targeted tutoring plan",
                        rank=1,
                        effort="High",
                        confidence=0.82,
                        expected_risk_reduction=0.14,
                        expected_new_risk_level="Safe",
                        expected_new_risk_score=0.39,
                        rationale="Focuses on the academic factors that currently contribute the most to risk.",
                        evidence=["Average grade is 58.0%."],
                    )
                ],
                cohort_comparison=CohortComparison(
                    cohort_size=12,
                    summary="This student is below the cohort baseline on one or more core metrics.",
                    average_risk_score=0.42,
                    average_avg_grade=66.5,
                    average_completion_rate=78.4,
                    risk_percentile=81.0,
                    performance_percentile=28.0,
                    completion_percentile=34.0,
                    metrics=[
                        CohortMetricComparison(
                            label="Average grade",
                            student_value=58.0,
                            cohort_average=66.5,
                            percentile=28.0,
                            direction="below",
                        )
                    ],
                ),
                fairness_evaluation=FairnessEvaluation(
                    parity_score=78.0,
                    summary="Parity score 78.0/100. One or more monitored groups show a meaningful risk disparity.",
                    overall_average_risk_score=0.42,
                    overall_elevated_risk_rate=58.0,
                    dimensions=[
                        FairnessDimensionCheck(
                            dimension="Learning Style",
                            current_group="Visual",
                            group_size=4,
                            average_risk_score=0.58,
                            cohort_average_risk_score=0.42,
                            disparity_score=0.16,
                            elevated_risk_rate=75.0,
                            status="action",
                            note="Learning Style group 'Visual' shows higher average risk than the cohort baseline across 4 students, with 75.0% in elevated risk bands.",
                        )
                    ],
                    alerts=[
                        FairnessAlert(
                            severity="high",
                            title="Learning Style disparity detected",
                            detail="Learning Style group 'Visual' shows higher average risk than the cohort baseline across 4 students, with 75.0% in elevated risk bands.",
                        )
                    ],
                ),
                explanation_stability=ExplanationStabilityEvaluation(
                    stability_score=84.0,
                    consistency_rate=88.0,
                    average_risk_shift=6.2,
                    confidence_band="Stable",
                    summary="The explanation remains largely consistent across small local perturbations.",
                    sensitive_features=[
                        StabilityFeatureSignal(
                            feature="Completion Rate",
                            tested_range="5%",
                            max_risk_shift=9.4,
                            outcome_changed=False,
                            sensitivity="Medium",
                        )
                    ],
                ),
                case_outcome_explorer=CaseOutcomeExplorer(
                    summary="Comparable cases show that targeted academic support usually prevents escalation.",
                    cases=[
                        CaseOutcomeExplorerEntry(
                            student_id="STU0012",
                            similarity_score=91.0,
                            trajectory="improving",
                            observed_outcome="Recovered to Safe",
                            latest_risk_level="Safe",
                            latest_risk_score=0.34,
                            learning_style="Visual",
                            recommended_action="Pair weekly tutoring with completion tracking.",
                            key_takeaway="Students with similar performance patterns improved when completion support was introduced early.",
                        )
                    ],
                ),
            )

        monkeypatch.setattr(
            student_insights_service,
            "build_insights",
            sample_build_insights,
        )

        response = client.post(
            "/api/v1/academic-risk/insights",
            json={
                "source": "connected",
                "institute_id": "LMS_INST_A",
                "request_payload": {
                    "student_id": "STU0003",
                    "avg_grade": 58.0,
                    "grade_consistency": 72.0,
                    "grade_range": 28.0,
                    "num_assessments": 5,
                    "assessment_completion_rate": 0.72,
                    "studied_credits": 60,
                    "num_of_prev_attempts": 0,
                    "low_performance": 0,
                    "low_engagement": 0,
                    "has_previous_attempts": 0,
                },
                "prediction": {
                    "student_id": "STU0003",
                    "risk_level": "Medium Risk",
                    "risk_score": 0.63,
                    "confidence": 0.84,
                    "probabilities": {
                        "Safe": 0.21,
                        "Medium Risk": 0.63,
                        "At-Risk": 0.16,
                    },
                    "recommendations": ["Schedule regular tutor check-ins."],
                    "top_risk_factors": [
                        {"feature": "avg_grade", "value": 58.0, "impact": "medium"}
                    ],
                    "prediction_id": "123e4567-e89b-12d3-a456-426614174111",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["similar_cases"][0]["student_id"] == "STU0008"
        assert data["interventions"][0]["title"] == "Targeted tutoring plan"
        assert data["cohort_comparison"]["cohort_size"] == 12
        assert data["fairness_evaluation"]["parity_score"] == 78.0
        assert data["explanation_stability"]["stability_score"] == 84.0
        assert data["case_outcome_explorer"]["cases"][0]["student_id"] == "STU0012"


class TestSyncPredictionEndpoint:
    """Tests for synced prediction endpoint."""

    def test_sync_predict_endpoint(self, client, monkeypatch):
        """Sync endpoint should return prediction payload when upstream mapping succeeds."""

        async def fake_build_prediction_request(student_id: str, days: int = 14):
            return PredictionRequest(
                student_id=student_id,
                total_interactions=120.0,
                avg_response_time=25.0,
                consistency_score=0.8,
                days_inactive=1,
                completion_rate=0.75,
                assessment_score=82.0,
                learning_style="Visual",
            )

        monkeypatch.setattr(
            sync_service, "build_prediction_request", fake_build_prediction_request
        )

        response = client.post("/api/v1/sync/predict/STU0001")
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "explanation" in data


class TestStudentInsightsServiceThresholds:
    """Focused checks for fairness threshold behavior."""

    def test_fairness_status_marks_moderate_disparity_as_watch(self):
        status = student_insights_service._fairness_status(
            disparity=0.047,
            group_size=4,
            elevated_rate=75.0,
            overall_elevated_rate=80.0,
        )

        assert status == "watch"

    def test_stability_sensitivity_uses_medium_for_non_flipping_shift(self):
        status = student_insights_service._stability_sensitivity(
            max_shift=18.5,
            outcome_changed=False,
        )

        assert status == "Medium"

    def test_safe_students_prioritize_same_band_similar_cases(self):
        current_request = AcademicRiskRequest(
            student_id="SAFE001",
            avg_grade=88.0,
            grade_consistency=91.0,
            grade_range=8.0,
            num_assessments=8,
            assessment_completion_rate=0.9,
            studied_credits=60,
            num_of_prev_attempts=0,
            low_performance=0,
            low_engagement=0,
            has_previous_attempts=0,
        )
        current_prediction = AcademicRiskResponse(
            student_id="SAFE001",
            risk_level="Safe",
            risk_score=0.08,
            confidence=0.91,
            probabilities={"Safe": 0.91, "Medium Risk": 0.07, "At-Risk": 0.02},
            recommendations=["Maintain current progress."],
            top_risk_factors=[],
        )

        safe_candidate = InsightCandidate(
            student_id="SAFE002",
            request=AcademicRiskRequest(
                student_id="SAFE002",
                avg_grade=84.0,
                grade_consistency=88.0,
                grade_range=10.0,
                num_assessments=8,
                assessment_completion_rate=0.86,
                studied_credits=60,
                num_of_prev_attempts=0,
                low_performance=0,
                low_engagement=0,
                has_previous_attempts=0,
            ),
            prediction=AcademicRiskResponse(
                student_id="SAFE002",
                risk_level="Safe",
                risk_score=0.11,
                confidence=0.88,
                probabilities={"Safe": 0.88, "Medium Risk": 0.09, "At-Risk": 0.03},
                recommendations=["Maintain consistent engagement."],
                top_risk_factors=[],
            ),
            learning_style="Visual",
            engagement_level="High",
        )

        at_risk_candidate = InsightCandidate(
            student_id="RISK001",
            request=AcademicRiskRequest(
                student_id="RISK001",
                avg_grade=42.0,
                grade_consistency=54.0,
                grade_range=36.0,
                num_assessments=4,
                assessment_completion_rate=0.5,
                studied_credits=60,
                num_of_prev_attempts=1,
                low_performance=0,
                low_engagement=1,
                has_previous_attempts=1,
            ),
            prediction=AcademicRiskResponse(
                student_id="RISK001",
                risk_level="At-Risk",
                risk_score=0.89,
                confidence=0.93,
                probabilities={"Safe": 0.03, "Medium Risk": 0.08, "At-Risk": 0.89},
                recommendations=["Escalate support immediately."],
                top_risk_factors=[],
            ),
            learning_style="Visual",
            engagement_level="Low",
        )

        safe_similarity = student_insights_service._similarity_score(
            current_request=current_request,
            current_prediction=current_prediction,
            current_learning_style="Visual",
            candidate=safe_candidate,
        )
        at_risk_similarity = student_insights_service._similarity_score(
            current_request=current_request,
            current_prediction=current_prediction,
            current_learning_style="Visual",
            candidate=at_risk_candidate,
        )

        assert safe_similarity > at_risk_similarity
