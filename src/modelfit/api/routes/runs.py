from uuid import UUID, uuid4

from celery import Celery
from fastapi import APIRouter, status

from modelfit.core.config import get_settings
from modelfit.core.schemas import EvaluationRunAccepted, EvaluationRunCreate, RunStatus

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post(
    "",
    response_model=EvaluationRunAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_run(payload: EvaluationRunCreate) -> EvaluationRunAccepted:
    settings = get_settings()
    run_id = uuid4()

    celery_client = Celery(broker=settings.redis_url)
    celery_client.send_task(
        "modelfit.execute_evaluation",
        kwargs={
            "run_id": str(run_id),
            "payload": payload.model_dump(mode="json"),
        },
    )

    return EvaluationRunAccepted(run_id=run_id, status=RunStatus.QUEUED)


@router.get("/{run_id}", response_model=EvaluationRunAccepted)
async def get_run(run_id: UUID) -> EvaluationRunAccepted:
    return EvaluationRunAccepted(run_id=run_id, status=RunStatus.QUEUED)
