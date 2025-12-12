"""
Database session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import settings
from models.database import Base

# Create engine with connection pooling
# Note: Neon pooler doesn't support statement_timeout in options
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    pool_size=5,         # Smaller pool for Neon's pooler
    max_overflow=10,     # Allow extra connections if needed
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {
        "connect_timeout": 10
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
