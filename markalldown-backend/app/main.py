"""FastAPI application entry point — Phase 1: Skeleton backend.

Implements:
- AC-11: GET /api/health
- AC-12: CORS hanya dari ALLOWED_ORIGINS
- AC-23: Semua error → JSON ApiError, tanpa stack trace / path server
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import get_config
from app.exceptions import AppError
from app.limiter import limiter
from app.models.schemas import ApiError
from app.routers import convert, health

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    cfg = get_config()

    app = FastAPI(
        title="markalldown API",
        description="Converter file/URL ke Markdown — SPEC-001",
        version=cfg.APP_VERSION,
        # Matikan docs di production (opsional)
        docs_url="/docs" if cfg.ENVIRONMENT != "production" else None,
        redoc_url=None,
    )

    # -----------------------------------------------------------------------
    # CORS — AC-12: hanya izinkan origin yang terdaftar
    # -----------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------------------------------------------------
    # Rate limiter state
    # -----------------------------------------------------------------------
    app.state.limiter = limiter

    # -----------------------------------------------------------------------
    # Exception handlers — AC-23: selalu JSON ApiError
    # -----------------------------------------------------------------------

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=ApiError(
                error="RATE_LIMITED",
                message="Terlalu banyak permintaan. Coba lagi nanti.",
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Log detail internal tapi JANGAN kirim ke klien (AC-23, NFR-S5)
        logger.debug("Validation error: %s", exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ApiError(
                error="INVALID_REQUEST",
                message="Data request tidak valid.",
            ).model_dump(),
        )

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiError(
                error=exc.error,
                message=exc.message,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
        # Log internal; JANGAN bocorkan stack trace / path ke klien (AC-23)
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiError(
                error="INTERNAL_ERROR",
                message="Terjadi kesalahan internal. Silakan coba lagi.",
            ).model_dump(),
        )

    # -----------------------------------------------------------------------
    # Routers
    # -----------------------------------------------------------------------
    app.include_router(health.router, prefix="/api")
    app.include_router(convert.router, prefix="/api")

    return app


app = create_app()
