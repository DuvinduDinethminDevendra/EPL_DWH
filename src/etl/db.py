"""SQLAlchemy engine/session helpers."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import database_url

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(database_url(), echo=False)
    return _engine


def get_session():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine())
    return _SessionLocal()
