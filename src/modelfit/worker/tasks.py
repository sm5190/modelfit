from typing import Any

from modelfit.orchestration.graph import evaluation_graph
from modelfit.worker.celery_app import celery_app


@celery_app.task(
    name="modelfit.execute_evaluation",
    bind=True,
    autoretry_for=(RuntimeError,),
    retry_backoff=True,
    max_retries=3,
)
def execute_evaluation(
    _self: Any,
    run_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return evaluation_graph.invoke(
        {
            "run_id": run_id,
            "payload": payload,
            "status": "queued",
            "events": [],
        }
    )
