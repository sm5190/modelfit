from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EvaluationEvidence:
    criterion: str
    score: float | None
    passed: bool | None
    rationale: str
    confidence: float
    evaluator_id: str
    evaluator_version: str


class Evaluator(Protocol):
    async def evaluate(self, response: str) -> list[EvaluationEvidence]: ...
