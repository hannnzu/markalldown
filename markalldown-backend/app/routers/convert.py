"""Router konversi — POST /api/convert/file, /api/convert/files, /api/convert/url.

Memenuhi:
- FR-1: Konversi satu file
- FR-2: Konversi batch file (1–20 file)
- FR-3, FR-4, FR-5, FR-6, FR-7, FR-8, FR-26, FR-27
- AC-1, AC-2, AC-3, AC-4, AC-6, AC-13, AC-24, AC-29, AC-31
- EC-1, EC-2, EC-3, EC-4, EC-5, EC-6, EC-7, EC-8, EC-17, EC-19
"""
from __future__ import annotations

import asyncio
import io
import logging
from datetime import UTC, datetime

from fastapi import APIRouter, File, Request, UploadFile

from app.config import get_config
from app.exceptions import AppError
from app.limiter import limiter
from app.models.schemas import BatchItem, ConvertFileResponse, ConvertFilesResponse
from app.services.converter import convert_file_data
from app.services.validators import read_and_validate_file_stream
from app.utils.file_utils import sanitize_filename

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/convert", tags=["convert"])


@router.post("/file", response_model=ConvertFileResponse)
@limiter.limit("30/minute")
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


@router.post("/files", response_model=ConvertFilesResponse)
@limiter.limit("30/minute")
async def convert_batch_files(
    request: Request,
    files: list[UploadFile] = File(default=[]),
) -> ConvertFilesResponse:
    """AC-4: Konversi batch file (1–20 file) ke Markdown."""
    cfg = get_config()

    if not files or len(files) == 0:
        raise AppError(
            status_code=422,
            error="NO_FILES",
            message="Tidak ada file yang diunggah.",
        )

    # Jika file tunggal yang dikirim berukuran 0 dan tanpa nama (mis. form kosong)
    if len(files) == 1 and not files[0].filename:
        raise AppError(
            status_code=422,
            error="NO_FILES",
            message="Tidak ada file yang diunggah.",
        )

    if len(files) > 20:
        raise AppError(
            status_code=422,
            error="TOO_MANY_FILES",
            message="Jumlah file melebihi batas maksimum 20 file.",
        )

    # Pra-baca dan validasi total ukuran seluruh batch (AC-31, EC-17)
    file_buffers: list[tuple[str, bytes]] = []
    total_batch_bytes = 0

    for upload in files:
        raw_name = upload.filename or "upload"
        sanitized_name = sanitize_filename(raw_name)
        chunks = []
        while True:
            chunk = await upload.read(64 * 1024)
            if not chunk:
                break
            total_batch_bytes += len(chunk)
            if total_batch_bytes > cfg.max_batch_size_bytes:
                raise AppError(
                    status_code=413,
                    error="BATCH_TOO_LARGE",
                    message=f"Total ukuran batch melebihi batas maksimum {cfg.MAX_BATCH_SIZE_MB} MB.",
                )
            chunks.append(chunk)
        file_buffers.append((sanitized_name, b"".join(chunks)))

    async def _process_item(name: str, content: bytes) -> BatchItem:
        try:
            # Validasi per-file
            data, ext = await read_and_validate_file_stream(
                stream=io.BytesIO(content),
                filename=name,
                max_size_bytes=cfg.max_file_size_bytes,
            )
            # Konversi
            markdown, _warnings = await convert_file_data(
                data=data,
                extension=ext,
                filename=name,
            )
            return BatchItem(
                filename=name,
                markdown=markdown,
                status="success",
            )
        except AppError as exc:
            return BatchItem(
                filename=name,
                markdown=None,
                status="error",
                error=exc.error,
                message=exc.message,
            )
        except Exception:
            logger.exception("Unexpected error in batch item %s", name)
            return BatchItem(
                filename=name,
                markdown=None,
                status="error",
                error="CONVERSION_FAILED",
                message=f"Gagal mengonversi file '{name}'.",
            )

    # Eksekusi dengan urutan yang sama (AC-4, NFR-P3)
    tasks = [_process_item(name, content) for name, content in file_buffers]
    results = await asyncio.gather(*tasks)

    success_count = sum(1 for item in results if item.status == "success")
    failed_count = sum(1 for item in results if item.status == "error")

    return ConvertFilesResponse(
        results=list(results),
        total=len(results),
        success=success_count,
        failed=failed_count,
    )
