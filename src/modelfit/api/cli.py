import uvicorn

from modelfit.core.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "modelfit.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.env == "development",
    )
