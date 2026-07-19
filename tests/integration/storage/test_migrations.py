"""Integration tests for ModelFit Alembic migrations."""

import asyncio
import os
import re
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import asyncpg
import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy.engine import URL, make_url

PROJECT_ROOT = Path(__file__).resolve().parents[3]

APPLICATION_TABLES = {
    "evaluation_sessions",
    "artifacts",
    "evaluation_runs",
    "model_runs",
}

SAFE_DATABASE_NAME = re.compile(r"^[a-z0-9_]+$")


def get_source_database_url() -> str:
    """Return a PostgreSQL URL when integration infrastructure is available."""
    database_url = os.getenv("MODELFIT_TEST_DATABASE_URL") or os.getenv("MODELFIT_DATABASE_URL")

    if database_url is None:
        pytest.skip(
            "PostgreSQL integration test requires "
            "MODELFIT_TEST_DATABASE_URL or MODELFIT_DATABASE_URL"
        )

    return database_url


def make_asyncpg_dsn(url: URL, database_name: str) -> str:
    """Convert a SQLAlchemy async URL into an asyncpg-compatible URL."""
    return url.set(
        drivername="postgresql",
        database=database_name,
    ).render_as_string(hide_password=False)


def make_test_database_url(
    source_database_url: str,
    database_name: str,
) -> str:
    """Return a SQLAlchemy URL pointing to the temporary test database."""
    return (
        make_url(source_database_url)
        .set(database=database_name)
        .render_as_string(hide_password=False)
    )


async def create_test_database(
    source_database_url: str,
    database_name: str,
) -> None:
    """Create an isolated PostgreSQL database for one test."""
    if SAFE_DATABASE_NAME.fullmatch(database_name) is None:
        raise ValueError("Unsafe test database name")

    source_url = make_url(source_database_url)
    admin_dsn = make_asyncpg_dsn(source_url, "postgres")

    admin_connection = await asyncpg.connect(admin_dsn)

    try:
        await admin_connection.execute(f'CREATE DATABASE "{database_name}"')
    finally:
        await admin_connection.close()

    test_dsn = make_asyncpg_dsn(source_url, database_name)
    test_connection = await asyncpg.connect(test_dsn)

    try:
        await test_connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
    finally:
        await test_connection.close()


async def drop_test_database(
    source_database_url: str,
    database_name: str,
) -> None:
    """Disconnect clients and remove the temporary test database."""
    if SAFE_DATABASE_NAME.fullmatch(database_name) is None:
        raise ValueError("Unsafe test database name")

    source_url = make_url(source_database_url)
    admin_dsn = make_asyncpg_dsn(source_url, "postgres")

    admin_connection = await asyncpg.connect(admin_dsn)

    try:
        await admin_connection.execute(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = $1
              AND pid <> pg_backend_pid()
            """,
            database_name,
        )

        await admin_connection.execute(f'DROP DATABASE IF EXISTS "{database_name}"')
    finally:
        await admin_connection.close()


@pytest.fixture
def isolated_database_url() -> Iterator[str]:
    """Create and later delete a unique PostgreSQL test database."""
    source_database_url = get_source_database_url()
    database_name = f"modelfit_test_{uuid4().hex}"

    asyncio.run(
        create_test_database(
            source_database_url,
            database_name,
        )
    )

    test_database_url = make_test_database_url(
        source_database_url,
        database_name,
    )

    try:
        yield test_database_url
    finally:
        asyncio.run(
            drop_test_database(
                source_database_url,
                database_name,
            )
        )


def run_alembic(
    database_url: str,
    *arguments: str,
) -> None:
    """Run the Alembic CLI against the isolated database."""
    environment = os.environ.copy()
    environment["MODELFIT_DATABASE_URL"] = database_url

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            *arguments,
        ],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        pytest.fail(
            "Alembic command failed.\n"
            f"Command: {' '.join(arguments)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def get_head_revision() -> str:
    """Return the latest revision declared by the migration scripts."""
    configuration = Config(str(PROJECT_ROOT / "alembic.ini"))
    scripts = ScriptDirectory.from_config(configuration)
    head_revision = scripts.get_current_head()

    if head_revision is None:
        raise RuntimeError("No Alembic head revision exists")

    return head_revision


async def read_schema_state(
    database_url: str,
) -> tuple[set[str], str | None]:
    """Read table names and the currently applied Alembic revision."""
    source_url = make_url(database_url)
    database_name = source_url.database

    if database_name is None:
        raise ValueError("Database URL does not contain a database name")

    connection = await asyncpg.connect(make_asyncpg_dsn(source_url, database_name))

    try:
        table_rows = await connection.fetch(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            """
        )

        table_names = {str(row["tablename"]) for row in table_rows}

        revision: str | None = None

        if "alembic_version" in table_names:
            revision_value = await connection.fetchval("SELECT version_num FROM alembic_version")

            if revision_value is not None:
                revision = str(revision_value)

        return table_names, revision
    finally:
        await connection.close()


@pytest.mark.integration
def test_migrations_upgrade_downgrade_and_reupgrade(
    isolated_database_url: str,
) -> None:
    """Verify the complete migration lifecycle on a clean database."""
    expected_head = get_head_revision()

    run_alembic(
        isolated_database_url,
        "upgrade",
        "head",
    )

    tables, revision = asyncio.run(read_schema_state(isolated_database_url))

    assert APPLICATION_TABLES.issubset(tables)
    assert revision == expected_head

    run_alembic(
        isolated_database_url,
        "downgrade",
        "base",
    )

    tables, revision = asyncio.run(read_schema_state(isolated_database_url))

    assert APPLICATION_TABLES.isdisjoint(tables)
    assert revision is None

    run_alembic(
        isolated_database_url,
        "upgrade",
        "head",
    )

    tables, revision = asyncio.run(read_schema_state(isolated_database_url))

    assert APPLICATION_TABLES.issubset(tables)
    assert revision == expected_head
