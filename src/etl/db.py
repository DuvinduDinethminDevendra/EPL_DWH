"""SQLAlchemy engine/session helpers."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker  # cSpell:ignore sessionmaker
from .config import database_url
from contextlib import contextmanager


#lazy initialization
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

@contextmanager
def get_db_session():
    session = get_session()
    try:
        yield session # provide the session to the caller
        session.commit() # commit if no exceptions
    except Exception:
        session.rollback() # rollback on error
        raise  # re-raise the exception
    finally:
        session.close() 