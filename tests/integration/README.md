# Integration tests

Integration tests will exercise PostgreSQL, Redis, MinIO, MCP servers, and
model-provider adapters through Docker Compose. Mark them with
`@pytest.mark.integration` so the fast pull-request suite remains lightweight.
