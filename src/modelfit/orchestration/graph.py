from langgraph.graph import END, START, StateGraph

from modelfit.orchestration.state import EvaluationState


def validate_request(state: EvaluationState) -> dict[str, object]:
    prompt = str(state["payload"].get("prompt", "")).strip()
    if not prompt:
        raise ValueError("Evaluation prompt cannot be empty.")

    return {
        "status": "validated",
        "events": [*state["events"], "request_validated"],
    }


def prepare_run(state: EvaluationState) -> dict[str, object]:
    return {
        "status": "prepared",
        "events": [*state["events"], "run_prepared"],
    }


def mark_scaffold_complete(state: EvaluationState) -> dict[str, object]:
    return {
        "status": "scaffold_complete",
        "events": [*state["events"], "workflow_scaffold_completed"],
    }


builder = StateGraph(EvaluationState)
builder.add_node("validate_request", validate_request)
builder.add_node("prepare_run", prepare_run)
builder.add_node("mark_scaffold_complete", mark_scaffold_complete)

builder.add_edge(START, "validate_request")
builder.add_edge("validate_request", "prepare_run")
builder.add_edge("prepare_run", "mark_scaffold_complete")
builder.add_edge("mark_scaffold_complete", END)

evaluation_graph = builder.compile()
