from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class ModelLicense(BaseModel):
    type: str
    identifier: str
    requires_acceptance: bool = False


class ModelDefinition(BaseModel):
    model_id: str
    role: str
    modalities: list[str]
    enabled: bool
    license: ModelLicense


def load_model_registry(
    path: Path = Path("configs/models.yaml"),
) -> dict[str, ModelDefinition]:
    raw: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {key: ModelDefinition.model_validate(value) for key, value in raw["models"].items()}
