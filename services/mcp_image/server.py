from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

DATA_ROOT = Path("/data").resolve()
mcp = FastMCP(
    "ModelFit Image Tools",
    host="0.0.0.0",
    port=9102,
    json_response=True,
    stateless_http=True,
)


class ImageDescription(BaseModel):
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
def image_server_health() -> dict[str, str]:
    """Return image MCP server status."""
    return {"service": "mcp-image", "status": "ok"}


@mcp.tool()
def image_describe_artifact(path: str) -> ImageDescription:
    """Describe an allowlisted image artifact under /data."""
    candidate = _safe_artifact_path(path)
    if candidate.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise ValueError("Unsupported image extension.")
    return ImageDescription(
        filename=candidate.name,
        extension=candidate.suffix.lower(),
        exists=candidate.exists(),
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
