"""Database connection and session management for XAI Prediction Service."""

import psycopg
from psycopg import sql
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings

DEFAULT_DB_URL = "postgresql+psycopg://postgres:admin@localhost:5432/xai-prediction"
DEFAULT_TEMP_DB_NAME = "temporary_students_db"


def _get_database_url() -> str:
    value = settings.DATABASE_URL
    if value is None or str(value).strip() == "":
        return DEFAULT_DB_URL
    return str(value).strip()


def _get_temp_students_database_url() -> str:
    value = settings.TEMP_STUDENTS_DATABASE_URL
    if value is not None and str(value).strip() != "":
        return str(value).strip()

    return make_url(_get_database_url()).set(database=DEFAULT_TEMP_DB_NAME).render_as_string(
        hide_password=False
    )


def _build_engine(database_url: str):
    return create_engine(
        database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False,
    )


engine = _build_engine(
    _get_database_url(),
)

temp_students_engine = _build_engine(
    _get_temp_students_database_url(),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TempStudentsSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=temp_students_engine
)
Base = declarative_base()
TempStudentsBase = declarative_base()


def _ensure_database_exists_for_url(database_url: str) -> str:
    """Create the configured PostgreSQL database if it does not already exist."""
    url = make_url(database_url)
    database_name = url.database

    if not database_name:
        raise ValueError("DATABASE_URL must include a database name")

    admin_database = "postgres" if database_name != "postgres" else database_name

    connect_kwargs = {
        "dbname": admin_database,
        "user": url.username,
        "password": url.password,
        "host": url.host,
        "port": url.port,
    }

    if url.query:
        connect_kwargs.update(url.query)

    with psycopg.connect(**connect_kwargs, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (database_name,),
            )
            exists = cursor.fetchone() is not None

            if not exists:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(database_name)
                    )
                )

    return database_name


def ensure_database_exists() -> str:
    return _ensure_database_exists_for_url(_get_database_url())


def ensure_temp_students_database_exists() -> str:
    return _ensure_database_exists_for_url(_get_temp_students_database_url())


def get_db():
    """Yield a request-scoped database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_temp_students_db():
    """Yield a request-scoped temporary-student database session."""
    db: Session = TempStudentsSessionLocal()
    try:
        yield db
    finally:
        db.close()
