"""Create database and tables for the XAI Prediction Service."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PROJECT_ROOT = ROOT.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import (
    Base,
    TempStudentsBase,
    engine,
    ensure_database_exists,
    ensure_temp_students_database_exists,
    temp_students_engine,
)
from app.models import (
    AcademicRiskPredictionRecord,
    TemporaryStudentPredictionRecord,
    TemporaryStudentRecord,
    XAIPredictionRecord,
)


def create_tables() -> None:
    """Create the target databases if needed, then create all XAI tables."""
    print("=" * 60)
    print("XAI PREDICTION SERVICE - DATABASE INITIALIZATION")
    print("=" * 60)
    print(f"Prediction database URL: {engine.url}")
    print(f"Temporary students database URL: {temp_students_engine.url}")

    prediction_database_name = ensure_database_exists()
    temp_database_name = ensure_temp_students_database_exists()
    print(f"Prediction database ready: {prediction_database_name}")
    print(f"Temporary students database ready: {temp_database_name}")

    Base.metadata.create_all(bind=engine)
    TempStudentsBase.metadata.create_all(bind=temp_students_engine)

    print("Prediction tables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")
    print("Temporary student tables created:")
    for table in TempStudentsBase.metadata.sorted_tables:
        print(f"  - {table.name}")
    print("Done.")


if __name__ == "__main__":
    create_tables()
