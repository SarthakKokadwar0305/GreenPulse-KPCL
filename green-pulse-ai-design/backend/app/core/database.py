"""
GreenPulse AI - Database Session & Engine Configuration
Supports asynchronous SQLite (local) and asynchronous PostgreSQL (production).
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import settings
from app.core.logging import logger

# Base Model for all SQLAlchemy entities
Base = declarative_base()

# Configure engine arguments
engine_kwargs = {"echo": settings.DB_ECHO}
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite specific parameter for thread checking
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Async engine creation
engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection helper providing scoped AsyncSession to request handlers."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session rollback triggered: {str(e)}")
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Creates database tables on startup if they don't exist, and ensures schema columns."""
    from sqlalchemy import text
    async with engine.begin() as conn:
        # Import all models to ensure metadata registration
        import app.models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)

        def migrate_schema(sync_conn):
            res = sync_conn.execute(text("PRAGMA table_info(users)"))
            cols = {row[1] for row in res.fetchall()}
            if cols:
                if "username" not in cols:
                    sync_conn.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR(100) DEFAULT ''"))
                if "status" not in cols:
                    sync_conn.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active'"))
                if "last_login" not in cols:
                    sync_conn.execute(text("ALTER TABLE users ADD COLUMN last_login DATETIME NULL"))

            rep_res = sync_conn.execute(text("PRAGMA table_info(reports)"))
            rep_cols = {row[1] for row in rep_res.fetchall()}
            if rep_cols and "summary_stats" not in rep_cols:
                sync_conn.execute(text("ALTER TABLE reports ADD COLUMN summary_stats JSON NULL"))

        try:
            await conn.run_sync(migrate_schema)
        except Exception as e:
            logger.warning(f"Schema migration note: {e}")

    logger.info("Database schema verified and initialized.")
