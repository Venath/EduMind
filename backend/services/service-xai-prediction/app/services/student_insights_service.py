"""Integrated insight generation for the XAI academic-risk flow."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import (
    AcademicRiskPredictionRecord,
    TemporaryStudentPredictionRecord,
    TemporaryStudentRecord,
)
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
    SimilarStudentCase,
    StabilityFeatureSignal,
    StudentInsightsRequest,
    StudentInsightsResponse,
)
from app.services.academic_risk_service import academic_risk_service
from app.services.sync_service import SyncServiceError, sync_service


@dataclass
class InsightCandidate:
    student_id: str
    request: AcademicRiskRequest
    prediction: AcademicRiskResponse
    learning_style: str | None = None
    engagement_level: str | None = None


class StudentInsightsService:
    """Build higher-level integrated XAI insights for the results page."""

    async def build_insights(
        self,
        payload: StudentInsightsRequest,
        db: Session,
        temp_db: Session,
    ) -> StudentInsightsResponse:
        source = payload.source.strip().lower()
        current_request = payload.request_payload
        current_prediction = payload.prediction

        if source == "connected":
            candidates, learning_style = await self._load_connected_candidates(
                payload=payload,
                db=db,
            )
        else:
            candidates, learning_style = self._load_temporary_candidates(
                payload=payload,
                temp_db=temp_db,
            )

        ranked_similar_candidates = self._rank_similar_candidates(
            current_request=current_request,
            current_prediction=current_prediction,
            current_learning_style=learning_style,
            candidates=candidates,
        )
        similar_cases = self._build_similar_cases(ranked_similar_candidates)
        interventions = await self._build_ranked_interventions(
            current_request=current_request,
            current_prediction=current_prediction,
            learning_style=learning_style,
        )
        cohort_comparison = self._build_cohort_comparison(
            current_request=current_request,
            current_prediction=current_prediction,
            candidates=candidates,
        )
        fairness_evaluation = self._build_fairness_evaluation(
            current_request=current_request,
            current_prediction=current_prediction,
            current_learning_style=learning_style,
            candidates=candidates,
        )
        explanation_stability = await self._build_explanation_stability(
            current_request=current_request,
            current_prediction=current_prediction,
        )
        case_outcome_explorer = await self._build_case_outcome_explorer(
            source=source,
            ranked_candidates=ranked_similar_candidates[:3],
            db=db,
            temp_db=temp_db,
        )

        return StudentInsightsResponse(
            student_id=current_request.student_id,
            source=source,
            similar_cases=similar_cases,
            interventions=interventions,
            cohort_comparison=cohort_comparison,
            fairness_evaluation=fairness_evaluation,
            explanation_stability=explanation_stability,
            case_outcome_explorer=case_outcome_explorer,
        )

    async def _load_connected_candidates(
        self,
        payload: StudentInsightsRequest,
        db: Session,
    ) -> tuple[list[InsightCandidate], str | None]:
        current_request = payload.request_payload
        current_prediction = payload.prediction
        institute_id = payload.institute_id or "LMS_INST_A"
        learning_style: str | None = None

        profile = await sync_service.fetch_learning_profile(current_request.student_id)
        if isinstance(profile, dict):
            learning_style = self._normalize_optional_string(profile.get("learning_style"))

        candidates = [
            InsightCandidate(
                student_id=current_request.student_id,
                request=current_request,
                prediction=current_prediction,
                learning_style=learning_style,
                engagement_level=None,
            )
        ]

        try:
            roster, profile_map = await sync_service.fetch_student_roster(
                institute_id=institute_id,
                limit=40,
            )
            for raw_student in roster:
                if self._extract_student_id(raw_student) == current_request.student_id:
                    candidates[0].engagement_level = self._normalize_optional_string(
                        raw_student.get("engagement_level")
                    )
                    break
            roster_candidates = await self._build_connected_candidates_from_roster(
                roster=roster,
                profile_map=profile_map,
                current_student_id=current_request.student_id,
            )
            if roster_candidates:
                candidates.extend(roster_candidates)
                if learning_style is None and current_request.student_id in profile_map:
                    learning_style = self._normalize_optional_string(
                        profile_map[current_request.student_id].get("learning_style")
                    )
                return self._dedupe_candidates(candidates), learning_style
        except SyncServiceError:
            pass

        candidates.extend(self._build_connected_candidates_from_history(db, current_request.student_id))
        return self._dedupe_candidates(candidates), learning_style

    async def _build_connected_candidates_from_roster(
        self,
        roster: list[dict[str, Any]],
        profile_map: dict[str, dict[str, Any]],
        current_student_id: str,
    ) -> list[InsightCandidate]:
        tasks = [
            self._build_connected_candidate(raw_student, profile_map.get(student_id))
            for raw_student in roster
            if (student_id := self._extract_student_id(raw_student))
            and student_id != current_student_id
        ]

        if not tasks:
            return []

        results = await asyncio.gather(*tasks, return_exceptions=True)
        candidates: list[InsightCandidate] = []
        for result in results:
            if isinstance(result, InsightCandidate):
                candidates.append(result)
        return candidates

    async def _build_connected_candidate(
        self,
        raw_student: dict[str, Any],
        profile: dict[str, Any] | None,
    ) -> InsightCandidate | None:
        student_id = self._extract_student_id(raw_student)
        if student_id is None:
            return None

        try:
            request = await sync_service.build_academic_risk_request(student_id=student_id, days=14)
            prediction = await academic_risk_service.predict(request)
        except Exception:
            return None

        return InsightCandidate(
            student_id=student_id,
            request=request,
            prediction=prediction,
            learning_style=(
                self._normalize_optional_string(profile.get("learning_style"))
                if isinstance(profile, dict)
                else None
            ),
            engagement_level=self._normalize_optional_string(raw_student.get("engagement_level")),
        )

    def _build_connected_candidates_from_history(
        self,
        db: Session,
        current_student_id: str,
    ) -> list[InsightCandidate]:
        records = (
            db.query(AcademicRiskPredictionRecord)
            .order_by(desc(AcademicRiskPredictionRecord.created_at))
            .all()
        )

        latest_by_student: dict[str, AcademicRiskPredictionRecord] = {}
        for record in records:
            if record.student_id not in latest_by_student and record.student_id != current_student_id:
                latest_by_student[record.student_id] = record

        candidates: list[InsightCandidate] = []
        for record in latest_by_student.values():
            if not isinstance(record.request_payload, dict) or not isinstance(record.response_payload, dict):
                continue
            try:
                request = AcademicRiskRequest.model_validate(record.request_payload)
                prediction = AcademicRiskResponse.model_validate(record.response_payload)
            except Exception:
                continue

            candidates.append(
                InsightCandidate(
                    student_id=record.student_id,
                    request=request,
                    prediction=prediction,
                )
            )

        return candidates

    def _load_temporary_candidates(
        self,
        payload: StudentInsightsRequest,
        temp_db: Session,
    ) -> tuple[list[InsightCandidate], str | None]:
        current_request = payload.request_payload
        current_prediction = payload.prediction
        candidates = [
            InsightCandidate(
                student_id=current_request.student_id,
                request=current_request,
                prediction=current_prediction,
                engagement_level=self._derive_engagement_level(current_request),
            )
        ]

        records = (
            temp_db.query(TemporaryStudentRecord)
            .order_by(
                desc(TemporaryStudentRecord.updated_at),
                desc(TemporaryStudentRecord.created_at),
            )
            .limit(30)
            .all()
        )

        for record in records:
            if record.student_id == current_request.student_id:
                continue
            if not isinstance(record.request_payload, dict) or not isinstance(record.response_payload, dict):
                continue
            try:
                request = AcademicRiskRequest.model_validate(record.request_payload)
                prediction = AcademicRiskResponse.model_validate(record.response_payload)
            except Exception:
                continue

            candidates.append(
                InsightCandidate(
                    student_id=record.student_id,
                    request=request,
                    prediction=prediction,
                    engagement_level=self._derive_engagement_level(request),
                )
            )

        return self._dedupe_candidates(candidates), None

    def _rank_similar_candidates(
        self,
        current_request: AcademicRiskRequest,
        current_prediction: AcademicRiskResponse,
        current_learning_style: str | None,
        candidates: list[InsightCandidate],
    ) -> list[tuple[float, InsightCandidate]]:
        ranked_candidates: list[tuple[float, InsightCandidate]] = []

        for candidate in candidates:
            if candidate.student_id == current_request.student_id:
                continue

            similarity = self._similarity_score(
                current_request=current_request,
                current_prediction=current_prediction,
                current_learning_style=current_learning_style,
                candidate=candidate,
            )
            ranked_candidates.append((similarity, candidate))

        ranked_candidates.sort(key=lambda item: item[0], reverse=True)
        return ranked_candidates

    def _build_similar_cases(
        self,
        ranked_candidates: list[tuple[float, InsightCandidate]],
    ) -> list[SimilarStudentCase]:
        similar_cases: list[SimilarStudentCase] = []
        for similarity, candidate in ranked_candidates[:3]:
            similar_cases.append(
                SimilarStudentCase(
                    student_id=candidate.student_id,
                    similarity_score=round(similarity, 3),
                    risk_level=candidate.prediction.risk_level,
                    risk_score=round(candidate.prediction.risk_score, 4),
                    avg_grade=round(candidate.request.avg_grade, 2),
                    completion_rate=round(candidate.request.assessment_completion_rate * 100.0, 2),
                    learning_style=candidate.learning_style,
                    engagement_level=candidate.engagement_level,
                    explanation=self._build_similarity_explanation_from_candidate(candidate),
                )
            )
        return similar_cases

    async def _build_ranked_interventions(
        self,
        current_request: AcademicRiskRequest,
        current_prediction: AcademicRiskResponse,
        learning_style: str | None,
    ) -> list[RankedIntervention]:
        scenarios = self._intervention_scenarios(current_request, learning_style)
        ranked: list[RankedIntervention] = []

        for title, effort, scenario_request, rationale, evidence in scenarios:
            simulated_prediction = await academic_risk_service.predict(scenario_request)
            expected_reduction = max(
                current_prediction.risk_score - simulated_prediction.risk_score,
                0.0,
            )
            confidence = min(
                0.95,
                0.55 + (0.08 * len(evidence)) + (expected_reduction * 0.6),
            )
            ranked.append(
                RankedIntervention(
                    title=title,
                    rank=1,
                    effort=effort,
                    confidence=round(confidence, 3),
                    expected_risk_reduction=round(expected_reduction, 4),
                    expected_new_risk_level=simulated_prediction.risk_level,
                    expected_new_risk_score=round(simulated_prediction.risk_score, 4),
                    rationale=rationale,
                    evidence=evidence,
                )
            )

        if not ranked:
            ranked.append(
                RankedIntervention(
                    title="Maintain current support plan",
                    rank=1,
                    effort="Low",
                    confidence=0.62,
                    expected_risk_reduction=0.0,
                    expected_new_risk_level=current_prediction.risk_level,
                    expected_new_risk_score=round(current_prediction.risk_score, 4),
                    rationale="The student is already in a stable band, so the best next step is to preserve consistency.",
                    evidence=[
                        f"Current risk is {current_prediction.risk_level}.",
                        f"Average grade is {current_request.avg_grade:.1f}%.",
                    ],
                )
            )

        ranked.sort(
            key=lambda item: (
                item.expected_risk_reduction,
                item.confidence,
                -self._effort_rank(item.effort),
            ),
            reverse=True,
        )

        for index, item in enumerate(ranked[:3], start=1):
            item.rank = index

        return ranked[:3]

    def _build_cohort_comparison(
        self,
        current_request: AcademicRiskRequest,
        current_prediction: AcademicRiskResponse,
        candidates: list[InsightCandidate],
    ) -> CohortComparison | None:
        if not candidates:
            return None

        unique_candidates = self._dedupe_candidates(candidates)
        risk_scores = [candidate.prediction.risk_score for candidate in unique_candidates]
        avg_grades = [candidate.request.avg_grade for candidate in unique_candidates]
        completion_rates = [
            candidate.request.assessment_completion_rate * 100.0
            for candidate in unique_candidates
        ]

        avg_risk = self._average(risk_scores)
        avg_grade = self._average(avg_grades)
        avg_completion = self._average(completion_rates)

        risk_percentile = self._percentile_rank(risk_scores, current_prediction.risk_score)
        performance_percentile = self._percentile_rank(avg_grades, current_request.avg_grade)
        completion_percentile = self._percentile_rank(
            completion_rates,
            current_request.assessment_completion_rate * 100.0,
        )

        metrics = [
            CohortMetricComparison(
                label="Average grade",
                student_value=round(current_request.avg_grade, 2),
                cohort_average=round(avg_grade, 2),
                percentile=round(performance_percentile, 1),
                direction=self._comparison_direction(current_request.avg_grade, avg_grade),
            ),
            CohortMetricComparison(
                label="Completion rate",
                student_value=round(current_request.assessment_completion_rate * 100.0, 2),
                cohort_average=round(avg_completion, 2),
                percentile=round(completion_percentile, 1),
                direction=self._comparison_direction(
                    current_request.assessment_completion_rate * 100.0,
                    avg_completion,
                ),
            ),
            CohortMetricComparison(
                label="Risk score",
                student_value=round(current_prediction.risk_score * 100.0, 2),
                cohort_average=round(avg_risk * 100.0, 2),
                percentile=round(risk_percentile, 1),
                direction=self._inverse_comparison_direction(
                    current_prediction.risk_score,
                    avg_risk,
                ),
            ),
        ]

        return CohortComparison(
            cohort_size=len(unique_candidates),
            summary=self._build_cohort_summary(
                current_prediction=current_prediction,
                avg_risk=avg_risk,
                performance_percentile=performance_percentile,
                completion_percentile=completion_percentile,
            ),
            average_risk_score=round(avg_risk, 4),
            average_avg_grade=round(avg_grade, 2),
            average_completion_rate=round(avg_completion, 2),
            risk_percentile=round(risk_percentile, 1),
            performance_percentile=round(performance_percentile, 1),
            completion_percentile=round(completion_percentile, 1),
            metrics=metrics,
        )

    def _build_fairness_evaluation(
        self,
        current_request: AcademicRiskRequest,
        current_prediction: AcademicRiskResponse,
        current_learning_style: str | None,
        candidates: list[InsightCandidate],
    ) -> FairnessEvaluation | None:
        unique_candidates = self._dedupe_candidates(candidates)
        if len(unique_candidates) < 2:
            return None

        overall_avg_risk = self._average(
            [candidate.prediction.risk_score for candidate in unique_candidates]
        )
        overall_elevated_rate = self._elevated_risk_rate(unique_candidates)

        dimensions: list[FairnessDimensionCheck] = []
        alerts: list[FairnessAlert] = []

        fairness_dimensions = [
            (
                "Learning Style",
                lambda candidate: candidate.learning_style or "Unknown",
                current_learning_style or "Unknown",
            ),
            (
                "Engagement Level",
                lambda candidate: candidate.engagement_level or self._derive_engagement_level(candidate.request),
                self._derive_engagement_level(current_request, unique_candidates[0].engagement_level),
            ),
            (
                "Performance Band",
                lambda candidate: self._performance_band(candidate.request.avg_grade),
                self._performance_band(current_request.avg_grade),
            ),
            (
                "Attempt History",
                lambda candidate: self._attempt_history_group(candidate.request),
                self._attempt_history_group(current_request),
            ),
        ]

        for dimension_name, group_getter, current_group in fairness_dimensions:
            grouped: dict[str, list[InsightCandidate]] = {}
            for candidate in unique_candidates:
                label = group_getter(candidate)
                grouped.setdefault(label, []).append(candidate)

            if len(grouped) < 2:
                continue

            group_members = grouped.get(current_group, [])
            if not group_members:
                continue

            group_avg_risk = self._average(
                [candidate.prediction.risk_score for candidate in group_members]
            )
            disparity = group_avg_risk - overall_avg_risk
            elevated_rate = self._elevated_risk_rate(group_members)
            status = self._fairness_status(
                disparity=disparity,
                group_size=len(group_members),
                elevated_rate=elevated_rate,
                overall_elevated_rate=overall_elevated_rate,
            )
            note = self._fairness_note(
                dimension=dimension_name,
                current_group=current_group,
                group_avg_risk=group_avg_risk,
                overall_avg_risk=overall_avg_risk,
                elevated_rate=elevated_rate,
                group_size=len(group_members),
            )

            dimensions.append(
                FairnessDimensionCheck(
                    dimension=dimension_name,
                    current_group=current_group,
                    group_size=len(group_members),
                    average_risk_score=round(group_avg_risk, 4),
                    cohort_average_risk_score=round(overall_avg_risk, 4),
                    disparity_score=round(disparity, 4),
                    elevated_risk_rate=round(elevated_rate, 1),
                    status=status,
                    note=note,
                )
            )

            if status != "balanced":
                alerts.append(
                    FairnessAlert(
                        severity="high" if status == "action" else "medium",
                        title=f"{dimension_name} disparity detected",
                        detail=note,
                    )
                )

        if not dimensions:
            return None

        max_gap = max(abs(item.disparity_score) for item in dimensions)
        parity_score = max(0.0, 100.0 - (max_gap * 250.0))

        return FairnessEvaluation(
            parity_score=round(parity_score, 1),
            summary=self._fairness_summary(
                parity_score=parity_score,
                alerts=alerts,
                overall_avg_risk=overall_avg_risk,
            ),
            overall_average_risk_score=round(overall_avg_risk, 4),
            overall_elevated_risk_rate=round(overall_elevated_rate, 1),
            dimensions=dimensions,
            alerts=alerts[:3],
        )

    async def _build_explanation_stability(
        self,
        current_request: AcademicRiskRequest,
        current_prediction: AcademicRiskResponse,
    ) -> ExplanationStabilityEvaluation:
        probes = [
            ("Average Grade", "avg_grade", 5.0, "points"),
            ("Grade Consistency", "grade_consistency", 5.0, "points"),
            ("Grade Range", "grade_range", 5.0, "points"),
            ("Completion Rate", "assessment_completion_rate", 0.05, "%"),
            ("Assessments", "num_assessments", 1.0, "count"),
        ]

        total_runs = 0
        consistent_runs = 0
        total_shift = 0.0
        feature_signals: list[StabilityFeatureSignal] = []

        for label, field, delta, unit in probes:
            probe_results: list[tuple[AcademicRiskResponse, float]] = []
            for direction in (-1.0, 1.0):
                current_value = float(getattr(current_request, field))
                updates: dict[str, Any]
                if field == "num_assessments":
                    updates = {
                        field: int(max(0, round(current_value + (direction * delta))))
                    }
                else:
                    updates = {
                        field: self._clamp(
                            current_value + (direction * delta),
                            0.0,
                            1.0 if field == "assessment_completion_rate" else 100.0,
                        )
                    }

                probe_request = self._clone_request(current_request, **updates)
                probe_prediction = await academic_risk_service.predict(probe_request)
                shift = abs(probe_prediction.risk_score - current_prediction.risk_score) * 100.0
                total_runs += 1
                total_shift += shift
                if probe_prediction.risk_level == current_prediction.risk_level:
                    consistent_runs += 1
                probe_results.append((probe_prediction, shift))

            max_shift = max((shift for _, shift in probe_results), default=0.0)
            outcome_changed = any(
                probe_prediction.risk_level != current_prediction.risk_level
                for probe_prediction, _ in probe_results
            )
            feature_signals.append(
                StabilityFeatureSignal(
                    feature=label,
                    tested_range=(
                        f"{delta * 100:.0f}%"
                        if field == "assessment_completion_rate"
                        else f"{delta:.0f} {unit}"
                    ),
                    max_risk_shift=round(max_shift, 1),
                    outcome_changed=outcome_changed,
                    sensitivity=self._stability_sensitivity(max_shift, outcome_changed),
                )
            )

        consistency_rate = (consistent_runs / total_runs) * 100.0 if total_runs else 100.0
        average_shift = total_shift / total_runs if total_runs else 0.0
        stability_score = self._clamp(
            consistency_rate - (average_shift * 0.8),
            0.0,
            100.0,
        )

        feature_signals.sort(
            key=lambda item: (item.outcome_changed, item.max_risk_shift),
            reverse=True,
        )

        return ExplanationStabilityEvaluation(
            stability_score=round(stability_score, 1),
            consistency_rate=round(consistency_rate, 1),
            average_risk_shift=round(average_shift, 1),
            confidence_band=self._stability_band(stability_score),
            summary=self._stability_summary(stability_score, feature_signals),
            sensitive_features=feature_signals[:4],
        )

    async def _build_case_outcome_explorer(
        self,
        source: str,
        ranked_candidates: list[tuple[float, InsightCandidate]],
        db: Session,
        temp_db: Session,
    ) -> CaseOutcomeExplorer | None:
        if not ranked_candidates:
            return None

        cases: list[CaseOutcomeExplorerEntry] = []
        for similarity, candidate in ranked_candidates:
            trajectory, observed_outcome, takeaway = await self._resolve_case_outcome(
                source=source,
                candidate=candidate,
                db=db,
                temp_db=temp_db,
            )
            cases.append(
                CaseOutcomeExplorerEntry(
                    student_id=candidate.student_id,
                    similarity_score=round(similarity * 100.0, 1),
                    trajectory=trajectory,
                    observed_outcome=observed_outcome,
                    latest_risk_level=candidate.prediction.risk_level,
                    latest_risk_score=round(candidate.prediction.risk_score, 4),
                    learning_style=candidate.learning_style,
                    recommended_action=(
                        candidate.prediction.recommendations[0]
                        if candidate.prediction.recommendations
                        else None
                    ),
                    key_takeaway=takeaway,
                )
            )

        return CaseOutcomeExplorer(
            summary=self._case_outcome_summary(cases),
            cases=cases,
        )

    async def _resolve_case_outcome(
        self,
        source: str,
        candidate: InsightCandidate,
        db: Session,
        temp_db: Session,
    ) -> tuple[str, str, str]:
        if source == "temporary":
            records = (
                temp_db.query(TemporaryStudentPredictionRecord)
                .filter(TemporaryStudentPredictionRecord.student_id == candidate.student_id)
                .order_by(desc(TemporaryStudentPredictionRecord.created_at))
                .limit(4)
                .all()
            )
            return self._summarize_record_history(
                [(float(record.risk_score), record.risk_level) for record in reversed(records)],
                candidate,
            )

        records = (
            db.query(AcademicRiskPredictionRecord)
            .filter(AcademicRiskPredictionRecord.student_id == candidate.student_id)
            .order_by(desc(AcademicRiskPredictionRecord.created_at))
            .limit(4)
            .all()
        )
        if records:
            return self._summarize_record_history(
                [(float(record.risk_score), record.risk_level) for record in reversed(records)],
                candidate,
            )

        try:
            timeline = await sync_service.build_connected_timeline(
                student_id=candidate.student_id,
                limit=4,
                days=30,
            )
            return self._summarize_record_history(
                [(float(point.risk_score), point.risk_level) for point in timeline.points],
                candidate,
            )
        except Exception:
            return (
                "insufficient_data",
                f"Current outcome is {candidate.prediction.risk_level}.",
                "Only a single comparable prediction is available for this case.",
            )

    def _summarize_record_history(
        self,
        history: list[tuple[float, str]],
        candidate: InsightCandidate,
    ) -> tuple[str, str, str]:
        if len(history) < 2:
            return (
                "insufficient_data",
                f"Current outcome is {candidate.prediction.risk_level}.",
                "Only a single comparable prediction is available for this case.",
            )

        first_score, first_level = history[0]
        latest_score, latest_level = history[-1]
        delta = latest_score - first_score

        if delta <= -0.05:
            trajectory = "improving"
        elif delta >= 0.05:
            trajectory = "worsening"
        else:
            trajectory = "stable"

        if trajectory == "improving" and latest_level == "Safe":
            observed_outcome = "Recovered to Safe"
        elif trajectory == "worsening" and latest_level != first_level:
            observed_outcome = f"Escalated to {latest_level}"
        elif trajectory == "stable":
            observed_outcome = f"Stayed {latest_level}"
        else:
            observed_outcome = f"Moved toward {latest_level}"

        takeaway = (
            candidate.prediction.recommendations[0]
            if candidate.prediction.recommendations
            else f"Monitor the same drivers that kept this case {latest_level.lower()}."
        )
        return trajectory, observed_outcome, takeaway

    def _similarity_score(
        self,
        current_request: AcademicRiskRequest,
        current_prediction: AcademicRiskResponse,
        current_learning_style: str | None,
        candidate: InsightCandidate,
    ) -> float:
        distance = 0.0
        distance += abs(current_request.avg_grade - candidate.request.avg_grade) / 100.0 * 0.30
        distance += (
            abs(
                current_request.assessment_completion_rate
                - candidate.request.assessment_completion_rate
            )
            * 0.25
        )
        distance += (
            abs(current_request.grade_consistency - candidate.request.grade_consistency)
            / 100.0
            * 0.15
        )
        distance += abs(current_request.grade_range - candidate.request.grade_range) / 100.0 * 0.10
        distance += (
            abs(current_request.num_assessments - candidate.request.num_assessments)
            / 20.0
            * 0.10
        )
        distance += abs(current_prediction.risk_score - candidate.prediction.risk_score) * 0.10

        if current_request.low_engagement != candidate.request.low_engagement:
            distance += 0.05
        if current_request.low_performance != candidate.request.low_performance:
            distance += 0.05
        if current_request.has_previous_attempts != candidate.request.has_previous_attempts:
            distance += 0.03

        current_band = self._risk_band_index(current_prediction.risk_level)
        candidate_band = self._risk_band_index(candidate.prediction.risk_level)
        band_gap = abs(current_band - candidate_band)
        if band_gap:
            distance += 0.12 * band_gap
            if current_band == 0 and candidate_band == 2:
                distance += 0.18
            elif current_band == 2 and candidate_band == 0:
                distance += 0.10

        similarity = max(0.0, 1.0 - distance)
        if current_learning_style and candidate.learning_style == current_learning_style:
            similarity = min(0.99, similarity + 0.05)
        return similarity

    def _build_similarity_explanation(
        self,
        current_request: AcademicRiskRequest,
        current_learning_style: str | None,
        candidate: InsightCandidate,
    ) -> str:
        reasons: list[str] = []
        if abs(current_request.avg_grade - candidate.request.avg_grade) <= 8:
            reasons.append("similar average grade band")
        if abs(
            current_request.assessment_completion_rate
            - candidate.request.assessment_completion_rate
        ) <= 0.1:
            reasons.append("matching completion pace")
        if abs(current_request.grade_consistency - candidate.request.grade_consistency) <= 10:
            reasons.append("close grade consistency")
        if current_learning_style and candidate.learning_style == current_learning_style:
            reasons.append(f"same {current_learning_style} learning style")

        if not reasons:
            return "Closest match across the current academic performance and XAI risk signals."

        rendered = ", ".join(reasons[:2])
        return f"Closest match due to {rendered}."

    def _build_similarity_explanation_from_candidate(
        self,
        candidate: InsightCandidate,
    ) -> str:
        reasons: list[str] = []
        if candidate.learning_style:
            reasons.append(f"{candidate.learning_style} learning style")
        if candidate.engagement_level:
            reasons.append(f"{candidate.engagement_level.lower()} engagement pattern")
        if candidate.request.assessment_completion_rate >= 0.8:
            reasons.append("strong completion pattern")
        if candidate.request.avg_grade < 40.0:
            reasons.append("low grade band")

        if not reasons:
            return "Closest match across the current academic performance and XAI risk signals."

        return f"Closest match due to {' and '.join(reasons[:2])}."

    def _intervention_scenarios(
        self,
        current_request: AcademicRiskRequest,
        learning_style: str | None,
    ) -> list[tuple[str, str, AcademicRiskRequest, str, list[str]]]:
        scenarios: list[tuple[str, str, AcademicRiskRequest, str, list[str]]] = []

        if current_request.avg_grade < 75 or current_request.low_performance == 1:
            boosted = self._clone_request(
                current_request,
                avg_grade=self._clamp(current_request.avg_grade + 8.0, 0.0, 100.0),
                grade_consistency=self._clamp(current_request.grade_consistency + 10.0, 0.0, 100.0),
                grade_range=self._clamp(current_request.grade_range - 8.0, 0.0, 100.0),
            )
            scenarios.append(
                (
                    "Targeted tutoring plan",
                    "High",
                    boosted,
                    "Focuses on the academic factors that currently contribute the most to risk.",
                    [
                        f"Average grade is {current_request.avg_grade:.1f}%.",
                        f"Grade consistency is {current_request.grade_consistency:.1f}%.",
                    ],
                )
            )

        if (
            current_request.assessment_completion_rate < 0.8
            or current_request.low_engagement == 1
        ):
            recovery = self._clone_request(
                current_request,
                assessment_completion_rate=self._clamp(
                    current_request.assessment_completion_rate + 0.2,
                    0.0,
                    1.0,
                ),
                num_assessments=max(current_request.num_assessments + 2, current_request.num_assessments),
                grade_consistency=self._clamp(current_request.grade_consistency + 5.0, 0.0, 100.0),
            )
            scenarios.append(
                (
                    "Completion recovery sprint",
                    "Medium",
                    recovery,
                    "Targets missing work and low participation, which often drive medium and high risk outcomes.",
                    [
                        f"Completion rate is {current_request.assessment_completion_rate * 100:.1f}%.",
                        f"Completed assessments count is {current_request.num_assessments}.",
                    ],
                )
            )

        if current_request.grade_consistency < 82 or current_request.grade_range > 20:
            structured = self._clone_request(
                current_request,
                grade_consistency=self._clamp(current_request.grade_consistency + 12.0, 0.0, 100.0),
                grade_range=self._clamp(current_request.grade_range - 10.0, 0.0, 100.0),
                num_assessments=max(current_request.num_assessments + 1, current_request.num_assessments),
                studied_credits=min(current_request.studied_credits + 15, 240),
            )
            scenarios.append(
                (
                    "Structured study plan",
                    "Medium",
                    structured,
                    "Aims to stabilize week-to-week performance and reduce volatility in results.",
                    [
                        f"Grade consistency is {current_request.grade_consistency:.1f}%.",
                        f"Grade range is {current_request.grade_range:.1f} points.",
                    ],
                )
            )

        if current_request.has_previous_attempts == 1 or current_request.num_of_prev_attempts > 0:
            reassessment = self._clone_request(
                current_request,
                avg_grade=self._clamp(current_request.avg_grade + 6.0, 0.0, 100.0),
                assessment_completion_rate=self._clamp(
                    current_request.assessment_completion_rate + 0.15,
                    0.0,
                    1.0,
                ),
                num_assessments=max(current_request.num_assessments + 1, current_request.num_assessments),
                grade_consistency=self._clamp(current_request.grade_consistency + 6.0, 0.0, 100.0),
            )
            scenarios.append(
                (
                    "Repeat-attempt support plan",
                    "High",
                    reassessment,
                    "Gives extra structure to students who are repeating the module or recovering from prior setbacks.",
                    [
                        f"Previous attempts count is {current_request.num_of_prev_attempts}.",
                    ],
                )
            )

        if learning_style:
            style_adjusted = self._clone_request(
                current_request,
                avg_grade=self._clamp(current_request.avg_grade + 4.0, 0.0, 100.0),
                grade_consistency=self._clamp(current_request.grade_consistency + 4.0, 0.0, 100.0),
                assessment_completion_rate=self._clamp(
                    current_request.assessment_completion_rate + 0.08,
                    0.0,
                    1.0,
                ),
            )
            scenarios.append(
                (
                    f"{learning_style} resource alignment",
                    "Low",
                    style_adjusted,
                    f"Recommends resources and check-ins tailored to the student's {learning_style.lower()} learning preference.",
                    [
                        f"Learning style profile is {learning_style}.",
                    ],
                )
            )

        return scenarios

    @staticmethod
    def _clone_request(
        request: AcademicRiskRequest,
        **updates: Any,
    ) -> AcademicRiskRequest:
        payload = request.model_dump()
        payload.update(updates)
        payload["low_performance"] = 1 if float(payload["avg_grade"]) < 40.0 else 0
        payload["low_engagement"] = (
            1 if float(payload["assessment_completion_rate"]) < 0.6 else 0
        )
        payload["has_previous_attempts"] = (
            1 if int(payload["num_of_prev_attempts"]) > 0 else 0
        )
        return AcademicRiskRequest.model_validate(payload)

    @staticmethod
    def _dedupe_candidates(candidates: list[InsightCandidate]) -> list[InsightCandidate]:
        seen: set[str] = set()
        deduped: list[InsightCandidate] = []
        for candidate in candidates:
            if candidate.student_id in seen:
                continue
            seen.add(candidate.student_id)
            deduped.append(candidate)
        return deduped

    @staticmethod
    def _extract_student_id(raw_student: dict[str, Any]) -> str | None:
        student_id = str(raw_student.get("student_id") or "").strip()
        return student_id or None

    @staticmethod
    def _average(values: list[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    @staticmethod
    def _percentile_rank(values: list[float], current_value: float) -> float:
        if not values:
            return 0.0
        count = sum(1 for value in values if value <= current_value)
        return (count / len(values)) * 100.0

    @staticmethod
    def _comparison_direction(student_value: float, cohort_average: float) -> str:
        delta = student_value - cohort_average
        if delta >= 2.0:
            return "above"
        if delta <= -2.0:
            return "below"
        return "aligned"

    @staticmethod
    def _inverse_comparison_direction(student_value: float, cohort_average: float) -> str:
        delta = student_value - cohort_average
        if delta <= -0.02:
            return "better"
        if delta >= 0.02:
            return "worse"
        return "aligned"

    def _build_cohort_summary(
        self,
        current_prediction: AcademicRiskResponse,
        avg_risk: float,
        performance_percentile: float,
        completion_percentile: float,
    ) -> str:
        if current_prediction.risk_score > avg_risk + 0.08:
            return "This student is trending riskier than the cohort and needs closer monitoring."
        if performance_percentile >= 60 and completion_percentile >= 60:
            return "This student is performing above the cohort baseline on both performance and completion."
        if performance_percentile <= 40 or completion_percentile <= 40:
            return "This student is below the cohort baseline on one or more core metrics."
        return "This student is broadly aligned with the current cohort baseline."

    @staticmethod
    def _stability_sensitivity(max_shift: float, outcome_changed: bool) -> str:
        if outcome_changed or max_shift >= 25.0:
            return "High"
        if max_shift >= 10.0:
            return "Medium"
        return "Low"

    @staticmethod
    def _stability_band(stability_score: float) -> str:
        if stability_score >= 85.0:
            return "High stability"
        if stability_score >= 65.0:
            return "Moderate stability"
        return "Low stability"

    @staticmethod
    def _stability_summary(
        stability_score: float,
        feature_signals: list[StabilityFeatureSignal],
    ) -> str:
        if not feature_signals:
            return "No local perturbation checks were required for this prediction."
        top_feature = feature_signals[0]
        if stability_score >= 85.0:
            return (
                f"The prediction stayed stable under small local changes. The most sensitive area was "
                f"{top_feature.feature}, but it did not materially destabilize the outcome."
            )
        if stability_score >= 65.0:
            return (
                f"The prediction is moderately stable. Small shifts in {top_feature.feature} move the "
                f"risk score the most and should be watched closely."
            )
        return (
            f"The prediction is sensitive to small changes. {top_feature.feature} had the strongest "
            f"local impact and may materially alter the explained outcome."
        )

    @staticmethod
    def _case_outcome_summary(cases: list[CaseOutcomeExplorerEntry]) -> str:
        if not cases:
            return "No comparable case outcomes are available yet."

        improving = sum(1 for case in cases if case.trajectory == "improving")
        worsening = sum(1 for case in cases if case.trajectory == "worsening")

        if improving > worsening:
            return "Most comparable cases improved over time, which suggests the current student has a plausible recovery path."
        if worsening > improving:
            return "Most comparable cases worsened over time, so the current student should be monitored closely for escalation."
        return "Comparable cases show mixed outcomes, so follow-up interventions should be evaluated carefully."

    @staticmethod
    def _normalize_optional_string(value: Any) -> str | None:
        rendered = str(value or "").strip()
        return rendered or None

    def _derive_engagement_level(
        self,
        request: AcademicRiskRequest,
        fallback: str | None = None,
    ) -> str:
        if fallback:
            return fallback
        if request.low_engagement == 1 or request.assessment_completion_rate < 0.6:
            return "Low"
        if request.assessment_completion_rate >= 0.85:
            return "High"
        return "Medium"

    @staticmethod
    def _performance_band(avg_grade: float) -> str:
        if avg_grade < 40.0:
            return "Below 40%"
        if avg_grade < 70.0:
            return "40-69%"
        return "70%+"

    @staticmethod
    def _attempt_history_group(request: AcademicRiskRequest) -> str:
        return "Has previous attempts" if request.num_of_prev_attempts > 0 else "First attempt"

    @staticmethod
    def _risk_band_index(risk_level: str) -> int:
        normalized = (risk_level or "").strip().lower()
        if "safe" in normalized:
            return 0
        if "medium" in normalized:
            return 1
        return 2

    @staticmethod
    def _is_elevated_risk(prediction: AcademicRiskResponse) -> bool:
        normalized = prediction.risk_level.strip().lower()
        return normalized in {"medium risk", "at-risk", "at risk", "high", "high risk"}

    def _elevated_risk_rate(self, candidates: list[InsightCandidate]) -> float:
        if not candidates:
            return 0.0
        elevated = sum(1 for candidate in candidates if self._is_elevated_risk(candidate.prediction))
        return (elevated / len(candidates)) * 100.0

    @staticmethod
    def _fairness_status(
        disparity: float,
        group_size: int,
        elevated_rate: float,
        overall_elevated_rate: float,
    ) -> str:
        if group_size < 2:
            return "balanced"

        absolute_gap = abs(disparity)
        elevated_gap = abs(elevated_rate - overall_elevated_rate)

        if group_size >= 3 and (absolute_gap >= 0.10 or elevated_gap >= 25.0):
            return "action"
        if absolute_gap >= 0.04 or elevated_gap >= 15.0:
            return "watch"
        return "balanced"

    def _fairness_note(
        self,
        dimension: str,
        current_group: str,
        group_avg_risk: float,
        overall_avg_risk: float,
        elevated_rate: float,
        group_size: int,
    ) -> str:
        if group_size < 2:
            return (
                f"{dimension} group '{current_group}' has limited sample coverage, so this parity "
                f"check is observational only."
            )
        direction = "higher" if group_avg_risk > overall_avg_risk else "lower"
        if abs(group_avg_risk - overall_avg_risk) < 0.02:
            direction = "aligned with"
        if direction == "aligned with":
            return (
                f"{dimension} group '{current_group}' is broadly aligned with the cohort baseline "
                f"across {group_size} students."
            )
        return (
            f"{dimension} group '{current_group}' shows {direction} average risk than the cohort "
            f"baseline across {group_size} students, with {elevated_rate:.1f}% in elevated risk bands."
        )

    @staticmethod
    def _fairness_summary(
        parity_score: float,
        alerts: list[FairnessAlert],
        overall_avg_risk: float,
    ) -> str:
        if alerts:
            return (
                f"Parity score {parity_score:.1f}/100. One or more monitored groups show a meaningful "
                f"risk disparity against the cohort average of {overall_avg_risk * 100:.1f}%."
            )
        return (
            f"Parity score {parity_score:.1f}/100. The monitored groups are broadly aligned with the "
            f"cohort average risk of {overall_avg_risk * 100:.1f}%."
        )

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))

    @staticmethod
    def _effort_rank(effort: str) -> int:
        normalized = effort.strip().lower()
        if normalized == "low":
            return 3
        if normalized == "medium":
            return 2
        if normalized == "high":
            return 1
        return 0


student_insights_service = StudentInsightsService()
