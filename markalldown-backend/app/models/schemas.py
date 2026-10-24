"""Pydantic schemas — kontrak API sesuai SPEC-001 API Contracts.

Setiap field, tipe, dan error code harus konsisten dengan API_SPEC.md.
Jika ada perbedaan, spec menang.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------

class ApiError(BaseModel):
    """Format error universal — AC-23: tanpa stack trace / path server."""
    error: str    # kode mesin (bahasa Inggris) — sesuai ErrorCode di spec
    message: str  # pesan untuk manusia (Bahasa Indonesia) — D-13


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str


# ---------------------------------------------------------------------------
# Convert file (single)
# ---------------------------------------------------------------------------

class ConvertFileResponse(BaseModel):
    filename: str          # tersanitasi, tanpa path
    markdown: str
    size_bytes: int        # ukuran file asli (>= 1)
    converted_at: str      # ISO 8601 UTC
    warnings: List[str] = []


# ---------------------------------------------------------------------------
# Convert files (batch)
# ---------------------------------------------------------------------------

class BatchItem(BaseModel):
    filename: str
    markdown: Optional[str] = None    # null jika status = error
    status: Literal["success", "error"]
    error: Optional[str] = None       # ErrorCode, hanya saat error
    message: Optional[str] = None     # pesan human-readable, hanya saat error


class ConvertFilesResponse(BaseModel):
    results: List[BatchItem]
    total: int
    success: int
    failed: int


# ---------------------------------------------------------------------------
# Convert URL
# ---------------------------------------------------------------------------

class ConvertUrlRequest(BaseModel):
    url: str  # http(s), max 2048 karakter


class ConvertUrlResponse(BaseModel):
    source_url: str
    markdown: str
    converted_at: str  # ISO 8601 UTC
