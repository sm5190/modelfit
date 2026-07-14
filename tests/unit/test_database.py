"""Tests for the asynchronous database foundation."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modelfit.storage.database import create_engine, create_session_factory


@pytest.mark.asyncio
async def test_create_engine_uses_explicit_database_url() -> None:
    database_url = "postgresql+asyncpg://user:password@database:5432/modelfit"

    engine = create_engine(database_url)

    try:
        assert engine.url.drivername == "postgresql+asyncpg"
        assert engine.url.host == "database"
        assert engine.url.port == 5432
        assert engine.url.database == "modelfit"
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_session_factory_configures_async_sessions() -> None:
    database_url = "postgresql+asyncpg://user:password@database:5432/modelfit"
    engine = create_engine(database_url)
    session_factory = create_session_factory(engine)

    try:
        async with session_factory() as session:
            assert isinstance(session, AsyncSession)
            assert session.sync_session.autoflush is False
            assert session.sync_session.expire_on_commit is False
    finally:
        await engine.dispose()
