# ADR 0002: MCP is a governed tool boundary

## Status

Accepted

## Decision

LangGraph does not permit candidate models to connect directly to arbitrary MCP
servers. ModelFit owns the MCP client, filters discovered tools, applies
per-session policy, records approvals, and stores tool-call evidence.

Local development may use stdio. Production services use Streamable HTTP.
Arbitrary end-user-provided MCP URLs are not supported.
