"""Initial durable persistence models for ModelFit."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modelfit.storage.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class EvaluationSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A user-facing workspace for one model comparison task."""

    __tablename__ = "evaluation_sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'active', 'completed', 'failed')",
            name="ck_evaluation_sessions_valid_status",
        ),
        Index(
            "ix_evaluation_sessions_status_created_at",
            "status",
            "created_at",
        ),
    )

    task_family: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="draft",
        server_default="draft",
    )

    tool_permissions: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    artifacts: Mapped[list[Artifact]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )

    evaluation_runs: Mapped[list[EvaluationRun]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class Artifact(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Metadata describing an uploaded or generated artifact."""

    __tablename__ = "artifacts"
    __table_args__ = (
        CheckConstraint(
            "size_bytes >= 0",
            name="nonnegative_size",
        ),
        Index(
            "ix_artifacts_session_created_at",
            "session_id",
            "created_at",
        ),
    )

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "evaluation_sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    object_key: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        unique=True,
    )

    mime_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    parser_version: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    session: Mapped[EvaluationSession] = relationship(
        back_populates="artifacts",
    )


class EvaluationRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A frozen execution of an evaluation configuration."""

    __tablename__ = "evaluation_runs"
    __table_args__ = (
        CheckConstraint(
            ("status IN ('pending', 'running', 'completed', 'partial', 'failed', 'cancelled')"),
            name="ck_evaluation_runs_valid_status",
        ),
        Index(
            "ix_evaluation_runs_session_status",
            "session_id",
            "status",
        ),
    )

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "evaluation_sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    frozen_request: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    environment_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    session: Mapped[EvaluationSession] = relationship(
        back_populates="evaluation_runs",
    )

    model_runs: Mapped[list[ModelRun]] = relationship(
        back_populates="evaluation_run",
        cascade="all, delete-orphan",
    )


class ModelRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One candidate model's execution within an evaluation run."""

    __tablename__ = "model_runs"
    __table_args__ = (
        CheckConstraint(
            ("status IN ('pending', 'running', 'completed', 'failed', 'timeout')"),
            name="ck_model_runs_valid_status",
        ),
        CheckConstraint(
            "input_tokens IS NULL OR input_tokens >= 0",
            name="nonnegative_input_tokens",
        ),
        CheckConstraint(
            "output_tokens IS NULL OR output_tokens >= 0",
            name="nonnegative_output_tokens",
        ),
        CheckConstraint(
            "latency_ms IS NULL OR latency_ms >= 0",
            name="nonnegative_latency",
        ),
        Index(
            "ix_model_runs_evaluation_run_status",
            "evaluation_run_id",
            "status",
        ),
    )

    evaluation_run_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "evaluation_runs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    model_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    model_revision: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    configuration: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    response_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    input_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    output_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    latency_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    tool_trace: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
    )

    evaluation_run: Mapped[EvaluationRun] = relationship(
        back_populates="model_runs",
    )
