from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

DATA_ROOT = Path("/data").resolve()
mcp = FastMCP(
    "ModelFit Document Tools",
    host="0.0.0.0",
    port=9101,
    json_response=True,
    stateless_http=True,
)


class ArtifactDescription(BaseModel):
    filename: str
    extension: str
    exists: bool


def _safe_artifact_path(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = DATA_ROOT / candidate
    resolved = candidate.resolve()
    if not resolved.is_relative_to(DATA_ROOT):
        raise ValueError("Artifact path must remain under /data.")
    return resolved


@mcp.tool()
def document_server_health() -> dict[str, str]:
    """Return document MCP server status."""
    return {"service": "mcp-document", "status": "ok"}


@mcp.tool()
def document_describe_artifact(path: str) -> ArtifactDescription:
    """Describe an allowlisted artifact under /data."""
    candidate = _safe_artifact_path(path)
    return ArtifactDescription(
        filename=candidate.name,
        extension=candidate.suffix.lower(),
        exists=candidate.exists(),
    )


@mcp.tool()
def document_extract_text(path: str) -> dict[str, str]:
    """Extract text from an allowlisted UTF-8 text file under /data.

    PDF and office-document parsing will be delegated to Docling in the
    document-processing milestone.
    """
    candidate = _safe_artifact_path(path)
    if candidate.suffix.lower() != ".txt":
        raise ValueError("Starter extractor currently accepts only .txt files.")
    return {"text": candidate.read_text(encoding="utf-8")}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
