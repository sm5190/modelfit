from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP(
    "ModelFit Web Tools",
    host="0.0.0.0",
    port=9103,
    json_response=True,
    stateless_http=True,
)


class SearchResult(BaseModel):
    title: str
    source: str
    snippet: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult] = Field(default_factory=list)
    status: str


@mcp.tool()
def web_server_health() -> dict[str, str]:
    """Return web MCP server status."""
    return {"service": "mcp-web", "status": "ok"}


@mcp.tool()
def web_search(query: str) -> SearchResponse:
    """Return a typed placeholder until an approved provider is configured."""
    return SearchResponse(
        query=query,
        status="provider_not_configured",
        results=[],
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
