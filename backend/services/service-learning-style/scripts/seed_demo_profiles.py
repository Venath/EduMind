"""
Seed demo student learning profiles so the learning-style service exposes
real student rows for XAI and dashboard lookups.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models import StudentLearningProfile
from scripts.seed_demo_data import DEMO_STUDENTS


STYLE_SEQUENCE = ["Visual", "Auditory", "Reading", "Kinesthetic", "Mixed"]
RESOURCE_TYPES = {
    "Visual": ["video", "tutorial", "cheatsheet"],
    "Auditory": ["video", "article"],
    "Reading": ["article", "cheatsheet", "quiz"],
    "Kinesthetic": ["interactive", "practice", "quiz"],
    "Mixed": ["video", "article", "interactive"],
}


def _style_probabilities(style: str) -> dict[str, float]:
    probs = {"Visual": 0.1, "Auditory": 0.1, "Reading": 0.1, "Kinesthetic": 0.1}
    if style == "Mixed":
        probs.update({"Visual": 0.25, "Auditory": 0.25, "Reading": 0.25, "Kinesthetic": 0.25})
    else:
        probs[style] = 0.7
    return probs


def seed_demo_profiles() -> None:
    db = SessionLocal()
    try:
        existing = (
            db.query(StudentLearningProfile.student_id)
            .filter(StudentLearningProfile.student_id.in_(DEMO_STUDENTS))
            .first()
        )
        if existing:
            print("Demo learning profiles already exist. Skipping.")
            return

        now = datetime.utcnow()
        for index, student_id in enumerate(DEMO_STUDENTS):
            style = STYLE_SEQUENCE[index % len(STYLE_SEQUENCE)]
            completion_rate = 55.0 + (index % 5) * 8.0
            profile = StudentLearningProfile(
                student_id=student_id,
                learning_style=style,
                style_confidence=0.82,
                style_probabilities=_style_probabilities(style),
                preferred_difficulty="Medium" if index % 3 else "Easy",
                preferred_resource_types=RESOURCE_TYPES[style],
                avg_completion_rate=min(95.0, completion_rate),
                total_resources_completed=4 + (index % 6),
                total_recommendations_received=6 + (index % 4),
                struggle_topics=["Machine Learning"] if index % 4 == 0 else ["Algorithms"],
                struggle_count=1 + (index % 3),
                days_tracked=14,
                last_activity_date=now - timedelta(days=index % 4),
                model_version="1.0",
            )
            db.add(profile)

        db.commit()
        print(f"Seeded demo learning profiles for {len(DEMO_STUDENTS)} students.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_profiles()
