"""Predictive bridge service for syncing features from upstream services."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.academic_risk import (
    AcademicRiskRequest,
    RiskTimelinePoint,
    RiskTimelineResponse,
)
from app.schemas.prediction import PredictionRequest
from app.schemas.student_lookup import (
    ConnectedStudentSearchResponse,
    ConnectedStudentSummary,
)
from app.services.academic_risk_service import academic_risk_service


@dataclass
class SyncServiceError(Exception):
    """Raised when upstream feature sync fails."""

    status_code: int
    detail: str


class XAIFeatureSyncService:
    """Collect and map features from engagement + learning-style services."""

    def __init__(self) -> None:
        self.engagement_base_url = settings.ENGAGEMENT_SERVICE_URL.rstrip("/")
        self.learning_style_base_url = settings.LEARNING_STYLE_SERVICE_URL.rstrip("/")

    async def build_prediction_request(
        self, student_id: str, days: int = 14
    ) -> PredictionRequest:
        latest_score, daily_metrics, profile = await self._fetch_upstream_data(
            student_id=student_id, days=days
        )
        return self._map_to_prediction_request(
            student_id=student_id,
            latest_score=latest_score,
            daily_metrics=daily_metrics,
            profile=profile,
        )

    async def build_academic_risk_request(
        self, student_id: str, days: int = 14
    ) -> AcademicRiskRequest:
        latest_score, history, daily_metrics, profile = await self._fetch_academic_upstream_data(
            student_id=student_id,
            days=days,
        )
        return self._map_to_academic_risk_request(
            student_id=student_id,
            latest_score=latest_score,
            history=history,
            daily_metrics=daily_metrics,
            profile=profile,
        )

    async def build_connected_timeline(
        self,
        student_id: str,
        limit: int = 8,
        days: int = 30,
    ) -> RiskTimelineResponse:
        latest_score, history, daily_metrics, profile = await self._fetch_academic_upstream_data(
            student_id=student_id,
            days=max(days, limit),
        )

        if not history:
            raise SyncServiceError(
                status_code=404,
                detail=f"Engagement history not found for student {student_id}",
            )

        normalized_history = self._normalize_entries_by_date(history)
        normalized_metrics = self._normalize_entries_by_date(daily_metrics)
        selected_history = self._select_timeline_entries(normalized_history, limit)
        points: list[RiskTimelinePoint] = []
        previous_request_payload: dict[str, Any] | None = None

        for entry in selected_history:
            if not isinstance(entry, dict):
                continue

            entry_date = self._extract_entry_date(entry)
            history_slice = self._history_until_date(normalized_history, entry_date)
            metrics_slice = self._metrics_until_date(normalized_metrics, entry_date)
            request = self._map_to_academic_risk_request(
                student_id=student_id,
                latest_score=entry,
                history=history_slice,
                daily_metrics=metrics_slice,
                profile=profile,
                timeline_mode=True,
            )
            prediction = await academic_risk_service.predict(request)
            request_payload = request.model_dump(mode="json")

            points.append(
                RiskTimelinePoint(
                    timestamp=self._timeline_timestamp(entry),
                    risk_level=prediction.risk_level,
                    risk_score=prediction.risk_score,
                    confidence=prediction.confidence,
                    avg_grade=request.avg_grade,
                    completion_rate=round(request.assessment_completion_rate * 100.0, 2),
                    key_driver=self._describe_timeline_driver(
                        previous_request_payload,
                        request_payload,
                    ),
                )
            )
            previous_request_payload = request_payload

        if not points:
            raise SyncServiceError(
                status_code=404,
                detail=f"Could not derive a connected timeline for student {student_id}",
            )

        latest_point = points[-1]
        return RiskTimelineResponse(
            student_id=student_id,
            total_points=len(points),
            trend_direction=self._get_trend_direction(points),
            timeline_basis="derived_history",
            latest_risk_level=latest_point.risk_level,
            latest_risk_score=latest_point.risk_score,
            points=points,
        )

    async def search_students(
        self,
        query: str = "",
        limit: int = 10,
        institute_id: str = "LMS_INST_A",
    ) -> ConnectedStudentSearchResponse:
        search_query = query.strip().lower()
        fetch_limit = min(max(limit * 5, 100), 1000)
        students_data, profile_map = await self.fetch_student_roster(
            institute_id=institute_id,
            limit=fetch_limit,
        )

        matches: list[ConnectedStudentSummary] = []
        for raw_student in students_data:
            if not isinstance(raw_student, dict):
                continue
            student_id = str(raw_student.get("student_id") or "").strip()
            if not student_id:
                continue
            if search_query and search_query not in student_id.lower():
                continue

            profile = profile_map.get(student_id)
            matches.append(
                ConnectedStudentSummary(
                    student_id=student_id,
                    engagement_score=round(
                        self._to_float(raw_student.get("engagement_score"), 0.0), 2
                    ),
                    engagement_level=str(raw_student.get("engagement_level") or "Unknown"),
                    engagement_trend=raw_student.get("engagement_trend"),
                    risk_level=str(raw_student.get("risk_level") or "Unknown"),
                    risk_probability=self._to_optional_probability(
                        raw_student.get("risk_probability")
                    ),
                    learning_style=(
                        str(profile.get("learning_style"))
                        if isinstance(profile, dict) and profile.get("learning_style")
                        else None
                    ),
                    avg_completion_rate=self._to_optional_percentage(
                        profile.get("avg_completion_rate") if isinstance(profile, dict) else None
                    ),
                    has_learning_profile=profile is not None,
                    last_updated=(
                        str(raw_student.get("last_updated"))
                        if raw_student.get("last_updated") is not None
                        else None
                    ),
                )
            )

        if search_query:
            matches.sort(key=lambda student: self._search_sort_key(student.student_id, search_query))
        else:
            matches.sort(key=lambda student: student.student_id)

        top_matches = matches[:limit]
        if top_matches:
            top_matches = await self._apply_xai_risk_preview(top_matches)

        return ConnectedStudentSearchResponse(
            query=query,
            total=len(matches),
            limit=limit,
            institute_id=institute_id,
            students=top_matches,
        )

    async def fetch_student_roster(
        self,
        institute_id: str,
        limit: int = 200,
    ) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
        timeout = httpx.Timeout(settings.SYNC_TIMEOUT_SECONDS)
        async with httpx.AsyncClient(timeout=timeout) as client:
            students_payload = await self._fetch_json(
                client=client,
                url=f"{self.engagement_base_url}/api/v1/students/list",
                service_name="engagement",
                not_found_detail="No students found in engagement service",
                params={"limit": limit, "institute_id": institute_id},
            )
            profiles_payload = await self._fetch_json_optional(
                client=client,
                url=f"{self.learning_style_base_url}/api/v1/students/",
                params={"limit": limit},
            )

        students_data = (
            students_payload.get("students") if isinstance(students_payload, dict) else None
        )
        if not isinstance(students_data, list):
            raise SyncServiceError(
                status_code=502,
                detail="Unexpected response format for engagement student list",
            )

        profile_map: dict[str, dict[str, Any]] = {}
        if isinstance(profiles_payload, list):
            for profile in profiles_payload:
                if not isinstance(profile, dict):
                    continue
                student_id = str(profile.get("student_id") or "").strip()
                if student_id:
                    profile_map[student_id] = profile

        return students_data, profile_map

    async def fetch_learning_profile(self, student_id: str) -> dict[str, Any] | None:
        timeout = httpx.Timeout(settings.SYNC_TIMEOUT_SECONDS)
        async with httpx.AsyncClient(timeout=timeout) as client:
            profile = await self._fetch_json_optional(
                client=client,
                url=f"{self.learning_style_base_url}/api/v1/students/{student_id}",
            )

        if profile is not None and not isinstance(profile, dict):
            return None
        return profile

    async def _apply_xai_risk_preview(
        self, students: list[ConnectedStudentSummary]
    ) -> list[ConnectedStudentSummary]:
        preview_tasks = [
            self._build_student_preview(student.student_id)
            for student in students
        ]
        preview_results = await asyncio.gather(*preview_tasks, return_exceptions=True)

        enriched_students: list[ConnectedStudentSummary] = []
        for student, preview in zip(students, preview_results, strict=False):
            if isinstance(preview, tuple):
                risk_level, risk_probability = preview
                enriched_students.append(
                    student.model_copy(
                        update={
                            "risk_level": risk_level,
                            "risk_probability": risk_probability,
                        }
                    )
                )
                continue

            enriched_students.append(student)

        return enriched_students

    async def _build_student_preview(self, student_id: str) -> tuple[str, float]:
        request = await self.build_academic_risk_request(student_id=student_id, days=14)
        prediction = await academic_risk_service.predict(request)
        return prediction.risk_level, prediction.risk_score

    async def _fetch_upstream_data(
        self, student_id: str, days: int
    ) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
        timeout = httpx.Timeout(settings.SYNC_TIMEOUT_SECONDS)
        async with httpx.AsyncClient(timeout=timeout) as client:
            latest_url = (
                f"{self.engagement_base_url}/api/v1/engagement/students/{student_id}/latest"
            )
            metrics_url = (
                f"{self.engagement_base_url}/api/v1/engagement/students/{student_id}/metrics"
            )
            profile_url = f"{self.learning_style_base_url}/api/v1/students/{student_id}"

            latest_task = self._fetch_json(
                client=client,
                url=latest_url,
                service_name="engagement",
                not_found_detail=f"Engagement data not found for student {student_id}",
            )
            metrics_task = self._fetch_json(
                client=client,
                url=metrics_url,
                service_name="engagement",
                not_found_detail=f"Engagement metrics not found for student {student_id}",
                params={"days": days},
            )
            profile_task = self._fetch_json(
                client=client,
                url=profile_url,
                service_name="learning-style",
                not_found_detail=f"Learning profile not found for student {student_id}",
            )

            latest_score, metrics_data, profile = await asyncio.gather(
                latest_task, metrics_task, profile_task
            )

        if not isinstance(metrics_data, list):
            raise SyncServiceError(
                status_code=502,
                detail="Unexpected response format for engagement metrics",
            )

        return latest_score, metrics_data, profile

    async def _fetch_academic_upstream_data(
        self, student_id: str, days: int
    ) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any] | None]:
        timeout = httpx.Timeout(settings.SYNC_TIMEOUT_SECONDS)
        async with httpx.AsyncClient(timeout=timeout) as client:
            latest_task = self._fetch_json(
                client=client,
                url=f"{self.engagement_base_url}/api/v1/engagement/students/{student_id}/latest",
                service_name="engagement",
                not_found_detail=f"Engagement data not found for student {student_id}",
            )
            history_task = self._fetch_json_optional(
                client=client,
                url=f"{self.engagement_base_url}/api/v1/engagement/students/{student_id}/history",
                params={"days": days},
            )
            metrics_task = self._fetch_json_optional(
                client=client,
                url=f"{self.engagement_base_url}/api/v1/engagement/students/{student_id}/metrics",
                params={"days": days},
            )
            profile_task = self._fetch_json_optional(
                client=client,
                url=f"{self.learning_style_base_url}/api/v1/students/{student_id}",
            )

            latest_score, history, metrics, profile = await asyncio.gather(
                latest_task,
                history_task,
                metrics_task,
                profile_task,
            )

        if history is None:
            history = [latest_score]
        if metrics is None:
            metrics = []

        if not isinstance(history, list):
            raise SyncServiceError(
                status_code=502,
                detail="Unexpected response format for engagement history",
            )
        if not isinstance(metrics, list):
            raise SyncServiceError(
                status_code=502,
                detail="Unexpected response format for engagement metrics",
            )
        if profile is not None and not isinstance(profile, dict):
            profile = None

        return latest_score, history, metrics, profile

    async def _fetch_json(
        self,
        client: httpx.AsyncClient,
        url: str,
        service_name: str,
        not_found_detail: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = await client.get(url, params=params)
        except httpx.RequestError as exc:
            raise SyncServiceError(
                status_code=502,
                detail=f"Could not reach {service_name} service: {exc}",
            ) from exc

        if response.status_code == 404:
            raise SyncServiceError(status_code=404, detail=not_found_detail)
        if response.status_code >= 400:
            raise SyncServiceError(
                status_code=502,
                detail=f"{service_name} service returned {response.status_code}",
            )

        try:
            return response.json()
        except ValueError as exc:
            raise SyncServiceError(
                status_code=502,
                detail=f"Invalid JSON returned by {service_name} service",
            ) from exc

    async def _fetch_json_optional(
        self,
        client: httpx.AsyncClient,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> Any | None:
        try:
            response = await client.get(url, params=params)
        except httpx.RequestError:
            return None

        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            return None

        try:
            return response.json()
        except ValueError:
            return None

    def _map_to_prediction_request(
        self,
        student_id: str,
        latest_score: dict[str, Any],
        daily_metrics: list[dict[str, Any]],
        profile: dict[str, Any],
    ) -> PredictionRequest:
        total_interactions = sum(
            float(metric.get("content_interactions") or 0.0)
            for metric in daily_metrics
            if isinstance(metric, dict)
        )

        total_session_minutes = sum(
            float(metric.get("total_session_duration_minutes") or 0.0)
            for metric in daily_metrics
            if isinstance(metric, dict)
        )
        avg_response_time = (
            (total_session_minutes * 60.0) / total_interactions
            if total_interactions > 0
            else 0.0
        )

        engagement_score = self._to_float(latest_score.get("engagement_score"), 50.0)
        consistency_raw = latest_score.get("rolling_avg_7days")
        if consistency_raw is None:
            consistency_raw = engagement_score

        consistency_score = self._to_ratio(consistency_raw, default=0.5)
        completion_rate = self._to_ratio(profile.get("avg_completion_rate"), default=0.5)
        days_inactive = self._days_since(latest_score.get("date"))

        return PredictionRequest(
            student_id=student_id,
            total_interactions=round(total_interactions, 2),
            avg_response_time=round(avg_response_time, 2),
            consistency_score=round(consistency_score, 4),
            days_inactive=days_inactive,
            completion_rate=round(completion_rate, 4),
            assessment_score=round(self._clamp(engagement_score, 0.0, 100.0), 2),
            learning_style=str(profile.get("learning_style") or ""),
        )

    def _map_to_academic_risk_request(
        self,
        student_id: str,
        latest_score: dict[str, Any],
        history: list[dict[str, Any]],
        daily_metrics: list[dict[str, Any]],
        profile: dict[str, Any] | None,
        timeline_mode: bool = False,
    ) -> AcademicRiskRequest:
        score_series = self._extract_score_series(history, timeline_mode=timeline_mode)
        avg_grade = round(sum(score_series) / len(score_series), 2) if score_series else 50.0
        grade_range = round((max(score_series) - min(score_series)), 2) if len(score_series) > 1 else 0.0
        grade_consistency = round(
            self._clamp(100.0 - grade_range, 0.0, 100.0),
            2,
        )

        num_assessments = sum(
            int(metric.get("quiz_attempts") or 0) + int(metric.get("assignments_submitted") or 0)
            for metric in daily_metrics
            if isinstance(metric, dict)
        )
        assessed_days = sum(
            1
            for metric in daily_metrics
            if isinstance(metric, dict)
            and (
                int(metric.get("quiz_attempts") or 0)
                + int(metric.get("assignments_submitted") or 0)
            )
            > 0
        )

        profile_completion = None
        if isinstance(profile, dict):
            profile_completion = profile.get("avg_completion_rate")

        if profile_completion is not None:
            assessment_completion_rate = self._to_ratio(profile_completion, default=0.5)
        elif daily_metrics:
            assessment_completion_rate = self._clamp(
                assessed_days / max(len(daily_metrics), 1),
                0.0,
                1.0,
            )
        else:
            assessment_completion_rate = 0.5

        engagement_score = self._to_float(latest_score.get("engagement_score"), 50.0)
        low_engagement = int(
            str(latest_score.get("engagement_level") or "").lower() == "low"
            or engagement_score < 40.0
        )
        low_performance = int(avg_grade < 40.0)

        return AcademicRiskRequest(
            student_id=student_id,
            avg_grade=round(self._clamp(avg_grade, 0.0, 100.0), 2),
            grade_consistency=grade_consistency,
            grade_range=round(self._clamp(grade_range, 0.0, 100.0), 2),
            num_assessments=max(num_assessments, 0),
            assessment_completion_rate=round(assessment_completion_rate, 4),
            studied_credits=60,
            num_of_prev_attempts=0,
            low_performance=low_performance,
            low_engagement=low_engagement,
            has_previous_attempts=0,
        )

    def _extract_score_series(
        self,
        history: list[dict[str, Any]],
        timeline_mode: bool = False,
    ) -> list[float]:
        if timeline_mode:
            assignment_scores = [
                self._to_float(item.get("assignment_score"), 0.0)
                for item in history
                if isinstance(item, dict) and item.get("assignment_score") is not None
            ]
            if assignment_scores and len({round(score, 4) for score in assignment_scores}) > 1:
                return assignment_scores

            engagement_scores = [
                self._to_float(item.get("engagement_score"), 0.0)
                for item in history
                if isinstance(item, dict)
            ]
            if engagement_scores and len({round(score, 4) for score in engagement_scores}) > 1:
                return engagement_scores

        assignment_scores = [
            self._to_float(item.get("assignment_score"), 0.0)
            for item in history
            if isinstance(item, dict)
        ]
        assignment_scores = [score for score in assignment_scores if score > 0]
        if assignment_scores:
            return assignment_scores

        engagement_scores = [
            self._to_float(item.get("engagement_score"), 0.0)
            for item in history
            if isinstance(item, dict)
        ]
        engagement_scores = [score for score in engagement_scores if score > 0]
        if engagement_scores:
            return engagement_scores

        return [50.0]

    def _history_until_date(
        self,
        history: list[dict[str, Any]],
        target_date: date | None,
    ) -> list[dict[str, Any]]:
        if target_date is None:
            return history
        return [
            item
            for item in history
            if isinstance(item, dict)
            and self._extract_entry_date(item) is not None
            and self._extract_entry_date(item) <= target_date
        ]

    def _metrics_until_date(
        self,
        metrics: list[dict[str, Any]],
        target_date: date | None,
    ) -> list[dict[str, Any]]:
        if target_date is None:
            return metrics
        return [
            item
            for item in metrics
            if isinstance(item, dict)
            and self._extract_entry_date(item) is not None
            and self._extract_entry_date(item) <= target_date
        ]

    def _timeline_timestamp(self, entry: dict[str, Any]) -> datetime:
        entry_date = self._extract_entry_date(entry)
        if entry_date is not None:
            return datetime.combine(entry_date, datetime.min.time())

        value = entry.get("created_at")
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        if isinstance(value, datetime):
            return value

        return datetime.utcnow()

    def _extract_entry_date(self, entry: dict[str, Any]) -> date | None:
        value = entry.get("date")
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                if "T" in value:
                    return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
                return date.fromisoformat(value)
            except ValueError:
                return None
        return None

    def _normalize_entries_by_date(
        self,
        entries: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        deduped_by_date: dict[date, dict[str, Any]] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            entry_date = self._extract_entry_date(entry)
            if entry_date is None:
                continue
            deduped_by_date[entry_date] = entry

        normalized_entries = list(deduped_by_date.values())
        normalized_entries.sort(key=lambda entry: self._extract_entry_date(entry) or date.min)
        return normalized_entries

    def _select_timeline_entries(
        self,
        history: list[dict[str, Any]],
        limit: int,
    ) -> list[dict[str, Any]]:
        if len(history) <= limit:
            return history

        indices: list[int] = []
        max_index = len(history) - 1
        for step in range(limit):
            candidate_index = round((step / max(limit - 1, 1)) * max_index)
            if candidate_index not in indices:
                indices.append(candidate_index)

        if len(indices) < limit:
            for candidate_index in range(len(history)):
                if candidate_index not in indices:
                    indices.append(candidate_index)
                if len(indices) == limit:
                    break

        indices.sort()
        return [history[index] for index in indices]

    def _describe_timeline_driver(
        self,
        previous_payload: dict[str, Any] | None,
        current_payload: dict[str, Any] | None,
    ) -> str:
        if not previous_payload or not current_payload:
            return "Baseline connected-student analysis derived from engagement history."

        timeline_fields = {
            "avg_grade": ("Average grade", 100.0, "points"),
            "grade_consistency": ("Grade consistency", 100.0, "points"),
            "grade_range": ("Grade range", 100.0, "points"),
            "assessment_completion_rate": ("Completion rate", 1.0, "%"),
            "num_assessments": ("Assessments completed", 20.0, ""),
        }

        top_change: tuple[str, str, float] | None = None
        for field, (label, scale, unit) in timeline_fields.items():
            previous_value = self._to_optional_float(previous_payload.get(field))
            current_value = self._to_optional_float(current_payload.get(field))
            if previous_value is None or current_value is None:
                continue

            delta = current_value - previous_value
            normalized_change = abs(delta) / scale if scale else abs(delta)
            if top_change is None or normalized_change > top_change[2]:
                rendered_delta = delta * 100.0 if field == "assessment_completion_rate" else delta
                top_change = (
                    label,
                    f"{rendered_delta:+.1f}{unit}".strip(),
                    normalized_change,
                )

        if top_change is None or top_change[2] < 0.02:
            return "Risk remained broadly stable across the connected engagement history."

        return f"Largest shift: {top_change[0]} changed by {top_change[1]}."

    def _get_trend_direction(self, points: list[RiskTimelinePoint]) -> str:
        if len(points) < 2:
            return "insufficient_data"

        delta = points[-1].risk_score - points[0].risk_score
        if delta >= 0.05:
            return "worsening"
        if delta <= -0.05:
            return "improving"
        return "stable"

    @staticmethod
    def _to_optional_float(value: Any) -> float | None:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_float(value: Any, default: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _to_ratio(value: Any, default: float) -> float:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return default

        if numeric > 1.0:
            numeric = numeric / 100.0

        return XAIFeatureSyncService._clamp(numeric, 0.0, 1.0)

    @staticmethod
    def _to_optional_percentage(value: Any) -> float | None:
        if value is None:
            return None
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None
        return round(XAIFeatureSyncService._clamp(numeric, 0.0, 100.0), 2)

    @staticmethod
    def _to_optional_probability(value: Any) -> float | None:
        if value is None:
            return None
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None
        return round(XAIFeatureSyncService._clamp(numeric, 0.0, 1.0), 4)

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))

    @staticmethod
    def _days_since(value: Any) -> int:
        if value is None:
            return 0

        parsed_date: date | None = None
        if isinstance(value, date):
            parsed_date = value
        elif isinstance(value, str):
            try:
                if "T" in value:
                    parsed_date = datetime.fromisoformat(
                        value.replace("Z", "+00:00")
                    ).date()
                else:
                    parsed_date = date.fromisoformat(value)
            except ValueError:
                parsed_date = None

        if parsed_date is None:
            return 0

        return max((date.today() - parsed_date).days, 0)

    @staticmethod
    def _search_sort_key(student_id: str, search_query: str) -> tuple[int, str]:
        normalized = student_id.lower()
        if normalized == search_query:
            return (0, student_id)
        if normalized.startswith(search_query):
            return (1, student_id)
        return (2, student_id)


sync_service = XAIFeatureSyncService()
