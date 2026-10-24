"""GET /api/health — AC-11, NFR-P1.

Endpoint sederhana; harus merespons < 200 ms (p95) tanpa dependensi eksternal.
"""
from fastapi import APIRouter

from app.config import get_config
from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """AC-11: Mengembalikan status layanan."""
    cfg = get_config()
    return HealthResponse(status="ok", version=cfg.APP_VERSION)
