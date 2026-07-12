from modelfit.orchestration.graph import evaluation_graph


def test_scaffold_graph_runs() -> None:
    result = evaluation_graph.invoke(
        {
            "run_id": "test-run",
            "payload": {
                "prompt": "Summarize this document.",
                "task_type": "summarization",
                "model_ids": ["phi_4_mini", "qwen3_8b"],
            },
            "status": "queued",
            "events": [],
        }
    )

    assert result["status"] == "scaffold_complete"
    assert result["events"][-1] == "workflow_scaffold_completed"
