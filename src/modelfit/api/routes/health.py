from fastapi import APIRouter

from modelfit import __version__
from modelfit.core.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(service="modelfit-api", status="ok", version=__version__)
