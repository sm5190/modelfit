# Model Runtime Compatibility Research

## Objective

Determine how ModelFit should invoke the Hugging Face models registered in
`configs/models.yaml` without requiring every developer to own a local GPU.

## Current repository state

Model definitions are stored in `configs/models.yaml`.

The repository contains a unit test that imports
`modelfit.models.registry.load_model_registry`, but the `modelfit.models`
package is not currently present on the main branch.

The current application settings define the default candidate models and Gemma
license acceptance, but they do not yet define a model provider, inference base
URL, runtime model name, authentication configuration, or inference timeout.

The missing package is:

```text
src/modelfit/models/
```

Because this package does not exist, the current model-registry test fails with:

```text
ModuleNotFoundError: No module named 'modelfit.models'
```

## Local development environment

The development machine uses:

- Windows
- WSL 2 with Ubuntu 22.04
- Docker Desktop
- VS Code Dev Containers
- Linux AMD64 containers

Docker itself is available on the WSL host:

```text
Docker client: 24.0.7
Docker Desktop engine: 24.0.7
```

Docker Model Runner is not currently available:

```text
docker: 'model' is not a docker command
```

The Docker CLI is also not installed inside the Dev Container.

Therefore, local ModelFit development must not require:

- Docker Model Runner
- a local GPU
- downloaded model weights
- a running inference server

Model-provider code must be testable using mocked HTTP responses.

## Questions investigated

For every configured model, this research considers:

1. Canonical Hugging Face model ID
2. Parameter size
3. Supported modalities
4. Context length
5. License and access restrictions
6. Quantized model availability
7. vLLM support
8. Docker Model Runner support
9. Local development feasibility
10. Recommended ModelFit role and runtime

## Model compatibility matrix

| Registry key | Hugging Face model | Role | Size | Modality | Context | License | Quantized options | vLLM | Docker Model Runner | Recommendation |
|---|---|---|---:|---|---|---|---|---|---|---|
| `phi_4_mini` | `microsoft/Phi-4-mini-instruct` | Candidate | 3.8B | Text | 128K | MIT | Available; no project-approved artifact selected | Documented | Documented | First model for a real text-generation smoke test |
| `qwen3_8b` | `Qwen/Qwen3-8B` | Candidate | 8.2B | Text | 32K native; 131K with YaRN | Apache-2.0 | Available; no project-approved artifact selected | Documented | Documented | Main general-purpose candidate |
| `gemma_3_12b` | `google/gemma-3-12b-it` | Candidate | 12B | Text and image | 128K input | Gemma license | Available; no project-approved artifact selected | Documented | Documented | Optional multimodal candidate after license acceptance |
| `qwen_2_5_vl` | `Qwen/Qwen2.5-VL-7B-Instruct` | Candidate | 8B | Text, image, and video | 32K configured | Apache-2.0 | Available; no project-approved artifact selected | Documented | Documented | First multimodal candidate |
| `prometheus_2` | `prometheus-eval/prometheus-7b-v2.0` | Primary judge | 7B | Text | Model-specific | Apache-2.0 with generated-data caveat | Limited community quantizations | Documented | Documented | Primary judge with a dedicated prompt adapter |
| `mistral_escalation` | `mistralai/Mistral-Small-3.1-24B-Instruct-2503` | Escalation judge | 24B | Text and image | 128K | Apache-2.0 | Quantized deployment is documented | Recommended | Not verified from the official card | Remote escalation judge only |

## Model findings

### Phi-4 Mini Instruct

Model ID:

```text
microsoft/Phi-4-mini-instruct
```

Key characteristics:

- 3.8 billion parameters
- text input and text output
- 128K-token context length
- MIT license
- Safetensors weights
- official vLLM instructions
- official Docker Model Runner instructions
- community quantizations available

Phi-4 Mini is the smallest model currently configured in ModelFit. It is the
most practical model for the first real model-serving integration.

Recommended use:

```text
Role: candidate
Preferred runtime: OpenAI-compatible vLLM endpoint
Optional runtime: Docker Model Runner
Local testing: mocked endpoint
```

### Qwen3 8B

Model ID:

```text
Qwen/Qwen3-8B
```

Key characteristics:

- 8.2 billion parameters
- text input and text output
- 32,768-token native context
- context extension to 131,072 tokens through YaRN
- Apache-2.0 license
- official vLLM instructions
- official Docker Model Runner instructions
- thinking and non-thinking modes
- community quantizations available

YaRN should not be enabled by default because static context scaling may reduce
performance on shorter inputs.

Qwen3 also supports thinking and non-thinking modes. ModelFit must record which
mode was used because it affects output length, latency, token usage, and
comparability.

Recommended use:

```text
Role: candidate
Preferred runtime: OpenAI-compatible vLLM endpoint
Default context: native context
Thinking mode: explicitly configured for each evaluation
```

### Gemma 3 12B Instruct

Model ID:

```text
google/gemma-3-12b-it
```

Key characteristics:

- 12 billion parameters
- text and image input
- text output
- 128K input context
- 8K output context
- Gemma custom license
- Hugging Face access requires accepting Google's terms
- official vLLM instructions
- official Docker Model Runner instructions
- community quantizations available

The model must remain disabled until license acceptance has been explicitly
recorded.

The current configuration correctly specifies:

```yaml
enabled: false
requires_acceptance: true
```

Recommended use:

```text
Role: optional multimodal candidate
Preferred runtime: remote vLLM
License requirement: explicit acceptance before use
Local testing: mocked endpoint
```

### Qwen2.5-VL 7B Instruct

Model ID:

```text
Qwen/Qwen2.5-VL-7B-Instruct
```

Key characteristics:

- approximately 8 billion parameters
- text, image, and video understanding
- text output
- 32,768-token configured context
- Apache-2.0 license
- official vLLM multimodal instructions
- official Docker Model Runner instructions
- community quantizations available

This model is relevant for:

- screenshot understanding
- chart interpretation
- document extraction
- invoice and form analysis
- visual question answering
- image-grounded evaluation tasks

Recommended use:

```text
Role: multimodal candidate
Preferred runtime: multimodal vLLM endpoint
Integration order: after text-only generation works
Local testing: mocked image and text requests
```

### Prometheus 2

Model ID:

```text
prometheus-eval/prometheus-7b-v2.0
```

Key characteristics:

- 7 billion parameters
- based on Mistral-Instruct
- text input and text output
- Apache-2.0 model license
- specialized for evaluating other language models
- supports absolute grading
- supports pairwise ranking
- official vLLM instructions
- official Docker Model Runner instructions

Prometheus is not a normal conversational candidate model.

Absolute grading requires:

1. Original instruction
2. Candidate response
3. Score rubric
4. Reference answer

Its expected output includes:

```text
Feedback: detailed feedback [RESULT] 4
```

Pairwise grading requires two candidate responses and returns a result such as:

```text
Feedback: comparative feedback [RESULT] A
```

Prometheus therefore needs a dedicated prompt builder and result parser.

The model card also states that Prometheus 2 and its feedback datasets are
subject to OpenAI terms for generated training data. This caveat must remain
visible in ModelFit's model metadata.

Recommended use:

```text
Role: primary judge
Preferred runtime: vLLM
Required integration: Prometheus-specific prompt adapter
Required parser: validated [RESULT] extraction
```

### Mistral Small 3.1 24B Instruct

Model ID:

```text
mistralai/Mistral-Small-3.1-24B-Instruct-2503
```

Key characteristics:

- 24 billion parameters
- text and image input
- text output
- 128K context
- Apache-2.0 license
- vLLM is officially recommended
- vLLM 0.8.1 or newer is recommended
- approximately 55 GB of GPU RAM is required for BF16 or FP16 inference
- quantized deployment can use substantially less memory

Docker Model Runner support was not verified from the official Mistral model
card during this research.

This model is not practical for the current local development machine.

Recommended use:

```text
Role: escalation judge
Preferred runtime: remote vLLM service
Local development: disabled
Failure behavior: preserve the primary-judge result and record escalation failure
```

## Approximate weight memory

The following values estimate model weights only.

They do not include:

- KV cache
- runtime buffers
- activations
- image encoders
- batching
- concurrency
- long-context memory

| Model | BF16 estimate | 8-bit estimate | 4-bit estimate |
|---|---:|---:|---:|
| Phi-4 Mini 3.8B | ~7.6 GB | ~3.8 GB | ~1.9 GB |
| Qwen3 8.2B | ~16.4 GB | ~8.2 GB | ~4.1 GB |
| Gemma 3 12B | ~24 GB | ~12 GB | ~6 GB |
| Qwen2.5-VL 8B | ~16 GB | ~8 GB | ~4 GB |
| Prometheus 2 7B | ~14 GB | ~7 GB | ~3.5 GB |
| Mistral Small 3.1 24B | ~48 GB | ~24 GB | ~12 GB |

Actual runtime memory will be higher than these estimates.

## Integration decision

ModelFit should not load Hugging Face model weights directly inside the
FastAPI process.

The application should communicate with a separate model-serving runtime
through an OpenAI-compatible HTTP interface.

```text
configs/models.yaml
        |
        v
Model Registry
        |
        v
Model Provider
        |
        v
OpenAI-compatible endpoint
        |
        +-- mocked endpoint for unit tests
        +-- vLLM
        +-- Docker Model Runner
        +-- hosted inference service
```

This allows ModelFit to change the inference runtime without changing the
evaluation workflow.

## Canonical model ID and served model name

ModelFit must distinguish between two identifiers.

Canonical Hugging Face model ID:

```text
Qwen/Qwen3-8B
```

Runtime-served model name:

```text
qwen3-8b
```

These values may be different.

The canonical model ID belongs in `configs/models.yaml`.

The served model name should come from runtime configuration.

## Local development recommendation

The current local development workflow should use:

```text
Unit tests:
    mocked OpenAI-compatible responses

Real integration testing:
    optional remote or hosted endpoint

Production-oriented serving:
    vLLM

Optional supported runtime:
    Docker Model Runner
```

No ordinary unit test should require:

- GPU hardware
- downloaded model weights
- Docker Model Runner
- vLLM
- external network access
- paid API credentials

## Final recommendation

The recommended ModelFit model roles are:

```text
First text integration model:
    Phi-4 Mini

Primary general candidate:
    Qwen3 8B

First multimodal candidate:
    Qwen2.5-VL 7B

Optional license-gated candidate:
    Gemma 3 12B

Primary judge:
    Prometheus 2

Remote escalation judge:
    Mistral Small 3.1 24B
```

ModelFit should use a provider-independent, OpenAI-compatible inference
boundary.

Docker Model Runner should be treated as an optional compatible runtime, not as
a requirement for local development.

## Sources

- https://huggingface.co/microsoft/Phi-4-mini-instruct
- https://huggingface.co/Qwen/Qwen3-8B
- https://huggingface.co/google/gemma-3-12b-it
- https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct
- https://huggingface.co/prometheus-eval/prometheus-7b-v2.0
- https://huggingface.co/mistralai/Mistral-Small-3.1-24B-Instruct-2503
- https://docs.docker.com/ai/model-runner/
- https://docs.docker.com/ai/model-runner/api-reference/
