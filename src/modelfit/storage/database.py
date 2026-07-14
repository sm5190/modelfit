"""Asynchronous SQLAlchemy engine and session management."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from modelfit.core.config import get_settings


def create_engine(database_url: str | None = None) -> AsyncEngine:
    """Create an asynchronous SQLAlchemy engine.

    An explicit URL can be supplied by tests and migration tooling. Application
    code normally uses the configured ModelFit database URL.
    """
    resolved_database_url = database_url or get_settings().database_url

    return create_async_engine(
        resolved_database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


def create_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create a session factory bound to the supplied engine."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )


@asynccontextmanager
async def session_scope(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    """Provide a transactional asynchronous database session.

    Successful work is committed. Exceptions trigger a rollback and are
    propagated to the caller.
    """
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
