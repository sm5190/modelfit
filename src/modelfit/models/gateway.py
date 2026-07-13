from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ModelRequest:
    prompt: str
    max_output_tokens: int = 800
    temperature: float = 0.2


@dataclass(frozen=True)
class ModelResponse:
    model_id: str
    content: str
    latency_ms: int
    input_tokens: int | None
    output_tokens: int | None
    error: str | None = None


class ModelGateway(Protocol):
    async def generate(self, model_id: str, request: ModelRequest) -> ModelResponse: ...
