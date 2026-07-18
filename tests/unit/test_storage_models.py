"""Tests for the initial ModelFit persistence models."""

from modelfit.storage.base import Base
from modelfit.storage.models import (
    Artifact,
    EvaluationRun,
    EvaluationSession,
    ModelRun,
)


def test_metadata_contains_initial_persistence_tables() -> None:
    expected_tables = {
        "evaluation_sessions",
        "artifacts",
        "evaluation_runs",
        "model_runs",
    }

    assert expected_tables.issubset(Base.metadata.tables)


def test_artifact_references_evaluation_session() -> None:
    foreign_key = next(iter(Artifact.__table__.c.session_id.foreign_keys))

    assert foreign_key.target_fullname == "evaluation_sessions.id"
    assert foreign_key.ondelete == "CASCADE"


def test_evaluation_run_references_session() -> None:
    foreign_key = next(iter(EvaluationRun.__table__.c.session_id.foreign_keys))

    assert foreign_key.target_fullname == "evaluation_sessions.id"
    assert foreign_key.ondelete == "CASCADE"


def test_model_run_references_evaluation_run() -> None:
    foreign_key = next(iter(ModelRun.__table__.c.evaluation_run_id.foreign_keys))

    assert foreign_key.target_fullname == "evaluation_runs.id"
    assert foreign_key.ondelete == "CASCADE"


def test_models_use_uuid_primary_keys() -> None:
    models = (
        EvaluationSession,
        Artifact,
        EvaluationRun,
        ModelRun,
    )

    for model in models:
        assert model.__table__.c.id.primary_key is True
