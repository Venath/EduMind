"""
Seed demo engagement metrics, scores, and predictions for Docker/dev environments.

The data is deterministic and scoped to the EduMind demo student IDs so XAI and
the admin dashboard have real records to query.
"""
from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models import DailyEngagementMetric, EngagementScore, DisengagementPrediction
from app.services.aggregation_service import compute_engagement_score, generate_prediction


DEMO_STUDENTS = [f"STU{i:04d}" for i in range(1, 26)]
DEMO_INSTITUTES = ["LMS_INST_A", "LMS_INST_B"]
SEED_DAYS = 14


def _student_profile(student_index: int) -> tuple[str, str]:
    bucket = student_index % 3
    trend_selector = student_index % 4
    profile = {0: "high", 1: "medium", 2: "low"}[bucket]
    trend = {0: "improving", 1: "stable", 2: "declining", 3: "stable"}[trend_selector]
    return profile, trend


def _base_metrics(profile: str) -> dict[str, float]:
    if profile == "high":
        return {
            "login_count": 4,
            "session_minutes": 100.0,
            "page_views": 10,
            "content_interactions": 8,
            "video_plays": 6,
            "forum_posts": 3,
            "forum_replies": 4,
            "quiz_attempts": 2,
            "assignments_submitted": 2,
            "resource_downloads": 3,
        }
    if profile == "medium":
        return {
            "login_count": 2,
            "session_minutes": 60.0,
            "page_views": 5,
            "content_interactions": 4,
            "video_plays": 3,
            "forum_posts": 1,
            "forum_replies": 2,
            "quiz_attempts": 1,
            "assignments_submitted": 1,
            "resource_downloads": 2,
        }
    return {
        "login_count": 1,
        "session_minutes": 20.0,
        "page_views": 2,
        "content_interactions": 1,
        "video_plays": 1,
        "forum_posts": 0,
        "forum_replies": 0,
        "quiz_attempts": 1,
        "assignments_submitted": 0,
        "resource_downloads": 0,
    }


def _apply_trend(value: float, trend: str, day_index: int) -> float:
    midpoint = SEED_DAYS // 2
    drift = day_index - midpoint
    if trend == "improving":
        return value + max(0, drift) * 2.5
    if trend == "declining":
        return max(0.0, value - max(0, drift) * 2.5)
    return value


def _apply_trend_int(value: int, trend: str, day_index: int) -> int:
    return max(0, int(round(_apply_trend(float(value), trend, day_index))))


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        existing = (
            db.query(EngagementScore.student_id)
            .filter(EngagementScore.student_id.in_(DEMO_STUDENTS))
            .first()
        )
        if existing:
            print("Demo engagement data already exists. Skipping.")
            return

        start_date = date.today() - timedelta(days=SEED_DAYS - 1)

        for institute_id in DEMO_INSTITUTES:
            for index, student_id in enumerate(DEMO_STUDENTS):
                profile, trend = _student_profile(index)
                base = _base_metrics(profile)

                for day_index in range(SEED_DAYS):
                    target_date = start_date + timedelta(days=day_index)

                    session_minutes = round(
                        _apply_trend(base["session_minutes"], trend, day_index), 2
                    )
                    login_count = _apply_trend_int(base["login_count"], trend, day_index)
                    page_views = _apply_trend_int(base["page_views"], trend, day_index)
                    content_interactions = _apply_trend_int(
                        base["content_interactions"], trend, day_index
                    )
                    video_plays = _apply_trend_int(base["video_plays"], trend, day_index)
                    forum_posts = _apply_trend_int(base["forum_posts"], trend, day_index)
                    forum_replies = _apply_trend_int(base["forum_replies"], trend, day_index)
                    quiz_attempts = _apply_trend_int(base["quiz_attempts"], trend, day_index)
                    assignments_submitted = _apply_trend_int(
                        base["assignments_submitted"], trend, day_index
                    )
                    resource_downloads = _apply_trend_int(
                        base["resource_downloads"], trend, day_index
                    )

                    metric = DailyEngagementMetric(
                        student_id=student_id,
                        institute_id=institute_id,
                        date=target_date,
                        login_count=login_count,
                        first_login_time=datetime.strptime("08:00", "%H:%M").time(),
                        last_login_time=datetime.strptime("18:00", "%H:%M").time(),
                        total_sessions=max(1, login_count),
                        total_session_duration_minutes=session_minutes,
                        avg_session_duration_minutes=round(
                            session_minutes / max(1, login_count), 2
                        ),
                        longest_session_minutes=round(
                            session_minutes / max(1, login_count), 2
                        ),
                        page_views=page_views,
                        unique_pages_viewed=page_views,
                        content_interactions=content_interactions,
                        video_plays=video_plays,
                        video_watch_minutes=round(video_plays * 5.0, 2),
                        resource_downloads=resource_downloads,
                        forum_posts=forum_posts,
                        forum_replies=forum_replies,
                        forum_reads=forum_posts + forum_replies + 1,
                        quiz_attempts=quiz_attempts,
                        quiz_score_sum=float(quiz_attempts * 75),
                        quiz_score_avg=75.0 if quiz_attempts else None,
                        assignments_submitted=assignments_submitted,
                        assignments_on_time=assignments_submitted,
                    )
                    db.add(metric)
                    db.flush()
                    compute_engagement_score(
                        db, student_id=student_id, target_date=target_date, institute_id=institute_id
                    )

                generate_prediction(db, student_id=student_id, institute_id=institute_id)

        db.commit()
        print(
            f"Seeded demo engagement data for {len(DEMO_STUDENTS)} students "
            f"across {len(DEMO_INSTITUTES)} institutes."
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
