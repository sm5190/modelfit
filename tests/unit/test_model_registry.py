from modelfit.models.registry import load_model_registry


def test_model_registry_loads() -> None:
    registry = load_model_registry()

    assert registry["qwen3_8b"].license.identifier == "Apache-2.0"
    assert registry["gemma_3_12b"].license.requires_acceptance is True
