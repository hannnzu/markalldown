"""Router konversi — POST /api/convert/file, /api/convert/files, /api/convert/url.

Memenuhi:
- FR-1: Konversi satu file
- FR-3, FR-4, FR-5, FR-7, FR-8, FR-26
- AC-1, AC-2, AC-3, AC-6, AC-13, AC-24, AC-29
- EC-1, EC-2, EC-3, EC-4, EC-5, EC-19
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, File, Request, UploadFile

from app.config import get_config
from app.models.schemas import ConvertFileResponse
from app.services.converter import convert_file_data
from app.services.validators import read_and_validate_file_stream
from app.utils.file_utils import sanitize_filename

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/convert", tags=["convert"])


@router.post("/file", response_model=ConvertFileResponse)
async def convert_single_file(
    request: Request,
    file: UploadFile = File(...),
) -> ConvertFileResponse:
    """AC-1: Konversi satu file ke Markdown."""
    cfg = get_config()

    raw_filename = file.filename or "upload"
    sanitized_filename = sanitize_filename(raw_filename)

    # Validasi berlapis dan membaca data
    data, ext = await read_and_validate_file_stream(
        stream=file.file,
        filename=sanitized_filename,
        max_size_bytes=cfg.max_file_size_bytes,
    )

    # Eksekusi konversi markitdown
    markdown, warnings = await convert_file_data(
        data=data,
        extension=ext,
        filename=sanitized_filename,
    )

    converted_at = datetime.now(UTC).isoformat()

    return ConvertFileResponse(
        filename=sanitized_filename,
        markdown=markdown,
        size_bytes=len(data),
        converted_at=converted_at,
        warnings=warnings,
    )
