from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from modelfit import __version__
from modelfit.api.routes import health, runs
from modelfit.core.config import get_settings
from modelfit.core.logging import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    yield


app = FastAPI(
    title="ModelFit API",
    description="Business-friendly LLM evaluation platform API.",
    version=__version__,
    lifespan=lifespan,
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(runs.router, prefix="/api/v1")
