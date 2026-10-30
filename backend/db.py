import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
try:
    from sqlalchemy.pool import StaticPool
except ImportError:
    StaticPool = None

DATABASE_URL = os.environ.get('DATABASE_URL') or "sqlite:///./yantrax.db"

# Create engine with check_same_thread disabled for SQLite in multi-threaded environments
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {},
    poolclass=StaticPool if DATABASE_URL.startswith('sqlite:///:memory:') else None,
    future=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_session():
    return SessionLocal()

def get_engine():
    global engine
    _database_url = os.environ.get('DATABASE_URL') or "sqlite:///./yantrax.db"
    if engine is None or str(engine.url) != _database_url:
        engine = create_engine(
            _database_url,
            connect_args={"check_same_thread": False} if _database_url.startswith('sqlite') else {},
            poolclass=StaticPool if (_database_url.startswith('sqlite:///:memory:') and StaticPool is not None) else None,
            future=True
        )
    return engine

def reset_engine():
    """Reset the engine and session factory - useful for tests that change DATABASE_URL."""
    global engine, SessionLocal, DATABASE_URL
    DATABASE_URL = os.environ.get('DATABASE_URL') or "sqlite:///./yantrax.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {},
        poolclass=StaticPool if (DATABASE_URL.startswith('sqlite:///:memory:') and StaticPool is not None) else None,
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
