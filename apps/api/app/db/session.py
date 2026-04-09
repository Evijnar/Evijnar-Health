# apps/api/app/db/session.py
"""
Database session management and connection pooling.
Handles SQLAlchemy engine initialization and async session creation.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.pool import NullPool, QueuePool
import logging

from app.config import settings
from app.models import Base

logger = logging.getLogger("evijnar.db")

# Global engine and session factory
_engine: AsyncEngine = None
_AsyncSessionLocal = None


async def init_db():
    """
    Initialize database engine and create all tables.
    Call this during app startup.
    """
    global _engine, _AsyncSessionLocal

    # PostgreSQL connection string for async
    # Convert postgresql:// to postgresql+asyncpg://
    db_url = settings.database_url
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    logger.info(f"Initializing database: {db_url.split('@')[1] if '@' in db_url else db_url}")

    try:
        # Create async engine with connection pooling
        _engine = create_async_engine(
            db_url,
            echo=settings.debug,  # Log all SQL statements if debug enabled
            pool_size=20,  # Number of connections to keep in pool
            max_overflow=10,  # Additional connections if pool exhausted
            pool_pre_ping=True,  # Test connections before using
            pool_recycle=3600,  # Recycle connections after 1 hour
        )

        # Create session factory
        _AsyncSessionLocal = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        # Create all tables
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ Database initialized successfully")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise


async def close_db():
    """
    Dispose of database engine connections.
    Call this during app shutdown.
    """
    global _engine

    if _engine:
        await _engine.dispose()
        logger.info("Database connection closed")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for injecting database session into routes.

    Usage in FastAPI:
        @app.get("/hospitals")
        async def get_hospitals(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(GlobalHospital))
            return result.scalars().all()
    """
    if not _AsyncSessionLocal:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with _AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Session error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()


def get_session_factory():
    """Get the session factory (useful for background tasks)"""
    if not _AsyncSessionLocal:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _AsyncSessionLocal
