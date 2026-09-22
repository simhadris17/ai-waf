"""
Database engine / session setup.

Supports both SQLite (local dev, default) and PostgreSQL (production).
SQLite is auto-detected from the DATABASE_URL and uses the correct
driver string. PostgreSQL URLs from Render/Heroku start with
postgres:// — we normalize them to postgresql+psycopg2:// automatically.
"""
import re

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import get_settings

settings = get_settings()


def _normalise_db_url(url: str) -> str:
    """Fix common URL issues:
    - Render/Heroku use 'postgres://' but SQLAlchemy requires 'postgresql://'
    - Add psycopg2 driver if not present for Postgres URLs
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


_db_url = _normalise_db_url(settings.DATABASE_URL)

# SQLite needs different connect_args; Postgres doesn't.
_is_sqlite = _db_url.startswith("sqlite")
_connect_args = {"check_same_thread": False} if _is_sqlite else {}

engine = create_engine(_db_url, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
