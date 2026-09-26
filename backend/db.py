import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get('DATABASE_URL') or "sqlite:///./yantrax.db"

# Create engine with check_same_thread disabled for SQLite in multi-threaded environments
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {},
    future=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_session():
    return SessionLocal()

def get_engine():
    return engine

def reset_engine():
    """Reset the engine and session factory - useful for tests that change DATABASE_URL."""
    global engine, SessionLocal
    DATABASE_URL = os.environ.get('DATABASE_URL') or "sqlite:///./yantrax.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {},
        future=True
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return engine

def init_db():
    """Create tables. This is safe to call on startup; Alembic will manage migrations in production."""
    try:
        from backend.models import Base
        Base.metadata.create_all(bind=engine)
    except Exception:
        # If models aren't available or DB inaccessible, log at caller
        raise
