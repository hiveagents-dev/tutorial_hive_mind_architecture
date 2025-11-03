"""Database connection and session management"""

import os
import logging
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://hivemind:hivemind_password@localhost:5432/hivemind"
)

# Create engine with JSON support
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=False,
    pool_pre_ping=True,  # Verify connections before using
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Database:
    """Database service for HiveMind persistence"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def init_tables(self):
        """Initialize database tables"""
        from .models import Base
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Database tables initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing database tables: {str(e)}")
            raise


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database on startup"""
    try:
        database = Database()
        database.init_tables()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️  Database initialization failed (will retry on first use): {str(e)}")
        # No lanzar excepción para permitir que la API arranque sin BD

