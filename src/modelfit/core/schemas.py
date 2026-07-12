from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class TaskType(StrEnum):
    SUMMARIZATION = "summarization"
    EXTRACTION = "extraction"
    EMAIL_WRITING = "email_writing"
    CODE_GENERATION = "code_generation"


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvaluationRunCreate(BaseModel):
    prompt: str = Field(min_length=1, max_length=20_000)
    task_type: TaskType
    model_ids: list[str] = Field(min_length=2, max_length=5)

    @field_validator("model_ids")
    @classmethod
    def model_ids_must_be_unique(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("model_ids must be unique")
        return value


class EvaluationRunAccepted(BaseModel):
    run_id: UUID = Field(default_factory=uuid4)
    status: RunStatus = RunStatus.QUEUED


class HealthResponse(BaseModel):
    service: str
    status: str
    version: str
