import asyncio

from app.schemas.academic_risk import AcademicRiskRequest
from app.services.academic_risk_service import AcademicRiskService


def build_service() -> AcademicRiskService:
    service = AcademicRiskService()
    service.model = None
    service.feature_names = service._get_default_features()
    service.metadata = {"model_type": "Demo Mode"}
    return service


def test_predict_includes_counterfactual_for_high_risk_student():
    service = build_service()
    request = AcademicRiskRequest(
        student_id="STU_COUNTER_1",
        avg_grade=35.0,
        grade_consistency=58.0,
        grade_range=42.0,
        num_assessments=3,
        assessment_completion_rate=0.45,
        studied_credits=60,
        num_of_prev_attempts=1,
        low_performance=1,
        low_engagement=1,
        has_previous_attempts=1,
    )

    response = asyncio.run(service.predict(request))

    assert response.counterfactual is not None
    assert response.counterfactual.current_outcome == response.risk_level
    assert response.counterfactual.target_outcome in {"Safe", "Medium Risk"}
    assert response.counterfactual.changes


def test_top_risk_factors_align_with_multiclass_labels():
    service = build_service()

    at_risk_request = AcademicRiskRequest(
        student_id="STU_COUNTER_2",
        avg_grade=38.0,
        grade_consistency=55.0,
        grade_range=35.0,
        num_assessments=3,
        assessment_completion_rate=0.5,
        studied_credits=60,
        num_of_prev_attempts=2,
        low_performance=1,
        low_engagement=1,
        has_previous_attempts=1,
    )
    medium_request = AcademicRiskRequest(
        student_id="STU_COUNTER_3",
        avg_grade=66.0,
        grade_consistency=74.0,
        grade_range=18.0,
        num_assessments=6,
        assessment_completion_rate=0.76,
        studied_credits=60,
        num_of_prev_attempts=0,
        low_performance=0,
        low_engagement=0,
        has_previous_attempts=0,
    )

    at_risk_factors = service._get_top_risk_factors(at_risk_request, 2)
    medium_factors = service._get_top_risk_factors(medium_request, 1)

    assert any(factor["feature"] == "avg_grade" for factor in at_risk_factors)
    assert any(factor["impact"] in {"critical", "high"} for factor in at_risk_factors)
    assert all(factor["impact"] != "critical" for factor in medium_factors)
