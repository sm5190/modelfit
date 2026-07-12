# ADR 0001: Start as a modular monolith with separate processes

## Status

Accepted

## Context

ModelFit needs multiple deployable processes, but splitting every domain into an independent repository or microservice would slow development and create premature operational coupling.

## Decision

Use one repository and one Python package with explicit domain modules. Run the UI, API, worker, and inference services as separate processes and containers.

## Consequences

- Shared schemas and domain logic remain consistent.
- Local development is simpler.
- Services can later be extracted behind existing module interfaces.
- Module boundaries must be enforced through reviews and tests.
