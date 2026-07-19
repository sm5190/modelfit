"""Alembic environment for ModelFit database migrations."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from modelfit.core.config import get_settings
from modelfit.storage.base import Base
from modelfit.storage.models import (
    Artifact,
    EvaluationRun,
    EvaluationSession,
    ModelRun,
)

# Alembic's configuration object, populated from alembic.ini.
config = context.config

# Configure Python logging from alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Importing the model classes registers their tables in Base.metadata.
_REGISTERED_MODELS = (
    EvaluationSession,
    Artifact,
    EvaluationRun,
    ModelRun,
)

# Read the database URL through ModelFit's normal settings system.
database_url = get_settings().database_url

# ConfigParser treats percent signs specially, so escape them for safety.
config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%"),
)

# Alembic compares this metadata against the current database schema.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Generate migration SQL without opening a database connection."""
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations using a synchronous connection adapter."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run Alembic migrations."""
    configuration = config.get_section(
        config.config_ini_section,
        {},
    )

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    try:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations while connected to the configured database."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
