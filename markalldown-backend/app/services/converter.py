"""Converter service — pembungkus markitdown untuk konversi dokumen ke Markdown.

Memenuhi:
- FR-1, FR-5: konversi 14 format
- FR-8, AC-24: memakai convert_stream(), TIDAK memakai convert() dengan input pengguna
- NFR-P3, D-9: semaphore konkurensi (3)
- NFR-R2, AC-15: timeout 60 detik -> 504 CONVERSION_TIMEOUT
- EC-3: error exception dipetakan ke 422 CONVERSION_FAILED
- EC-4: hasil kosong -> warnings ["NO_TEXT_EXTRACTED"]
"""
from __future__ import annotations

import asyncio
import io
import logging

from markitdown import MarkItDown, StreamInfo

from app.exceptions import AppError

logger = logging.getLogger(__name__)

# Semaphore konkurensi maks 3 proses konversi simultan (NFR-P3, D-9)
_SEMAPHORE = asyncio.Semaphore(3)
_TIMEOUT_SECONDS = 60.0


def _sync_convert_stream(data: bytes, extension: str, filename: str) -> str:
    """Fungsi sinkron konversi stream file di worker thread (FR-8, AC-24)."""
    md = MarkItDown()
    stream = io.BytesIO(data)
    info = StreamInfo(extension=extension, filename=filename)

    try:
        result = md.convert_stream(stream, stream_info=info)
        return result.text_content or ""
    except Exception as exc:
        logger.warning("markitdown convert_stream failed for %s: %s", filename, exc)
        raise AppError(
            status_code=422,
            error="CONVERSION_FAILED",
            message=f"Gagal mengonversi file '{filename}'. Pastikan file tidak rusak atau terproteksi kata sandi.",
        ) from exc


async def convert_file_data(
    data: bytes,
    extension: str,
    filename: str,
) -> tuple[str, list[str]]:
    """Konversi data file ke Markdown dengan pengamanan timeout dan semaphore.

    Mengembalikan (markdown_text, warnings).
    """
    async with _SEMAPHORE:
        try:
            markdown = await asyncio.wait_for(
                asyncio.to_thread(_sync_convert_stream, data, extension, filename),
                timeout=_TIMEOUT_SECONDS,
            )
        except TimeoutError as exc:
            logger.error("Conversion timed out after %s seconds for %s", _TIMEOUT_SECONDS, filename)
            raise AppError(
                status_code=504,
                error="CONVERSION_TIMEOUT",
                message="Waktu konversi melebihi batas 60 detik.",
            ) from exc

    warnings: list[str] = []
    # EC-4: PDF hasil scan tanpa lapisan teks mengembalikan string kosong
    if not markdown.strip():
        warnings.append("NO_TEXT_EXTRACTED")
        markdown = ""

    return markdown, warnings
