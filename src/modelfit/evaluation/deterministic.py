from modelfit.evaluation.base import EvaluationEvidence


def non_empty_response(response: str) -> EvaluationEvidence:
    passed = bool(response.strip())
    return EvaluationEvidence(
        criterion="non_empty_response",
        score=None,
        passed=passed,
        rationale="The response contains content." if passed else "The response is empty.",
        confidence=1.0,
        evaluator_id="deterministic.non_empty",
        evaluator_version="1.0.0",
    )
