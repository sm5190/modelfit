from typing import Any, TypedDict


class EvaluationState(TypedDict):
    run_id: str
    payload: dict[str, Any]
    status: str
    events: list[str]
