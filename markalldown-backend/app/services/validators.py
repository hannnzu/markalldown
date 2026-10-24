"""File validators — SPEC-001 D-12: validasi file berlapis.

Urutan validasi:
1. Allowlist ekstensi (case-insensitive, FR-3, EC-19) -> 415 UNSUPPORTED_FILE_TYPE
2. File kosong (EC-1) -> 422 EMPTY_FILE
3. Batas ukuran saat membaca per chunk (FR-4, AC-3) -> 413 FILE_TOO_LARGE
4. Magic bytes untuk format biner (FR-26, AC-29, EC-2) -> 422 INVALID_FILE_CONTENT
5. Pra-pindai ZIP jika file adalah arsip (NFR-S4, AC-14, AC-32, EC-18) -> 422 ARCHIVE_*
"""
from __future__ import annotations

import io
import os
import zipfile
from typing import BinaryIO

from app.exceptions import AppError

# 14 format inti yang didukung (FR-5, D-2)
ALLOWED_EXTENSIONS: set[str] = {
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".xls",
    ".csv",
    ".html",
    ".htm",
    ".json",
    ".xml",
    ".txt",
    ".md",
    ".epub",
    ".zip",
}

# Magic bytes untuk format biner (FR-26)
MAGIC_BYTES = {
    ".pdf": b"%PDF-",
    ".docx": b"PK\x03\x04",
    ".pptx": b"PK\x03\x04",
    ".xlsx": b"PK\x03\x04",
    ".epub": b"PK\x03\x04",
    ".zip": b"PK\x03\x04",
    ".xls": b"\xd0\xcf\x11\xe0",
}

MAX_ZIP_ENTRIES = 100
MAX_ZIP_UNCOMPRESSED_BYTES = 200 * 1024 * 1024  # 200 MB


def get_extension(filename: str) -> str:
    """Mengambil ekstensi file dalam huruf kecil dengan titik di depan."""
    _, ext = os.path.splitext(filename)
    return ext.lower()


def validate_extension(filename: str) -> str:
    """Validasi allowlist ekstensi (FR-3, EC-19)."""
    ext = get_extension(filename)
    if not ext or ext not in ALLOWED_EXTENSIONS:
        raise AppError(
            status_code=415,
            error="UNSUPPORTED_FILE_TYPE",
            message=f"Format file '{ext or filename}' tidak didukung.",
        )
    return ext


async def read_and_validate_file_stream(
    stream: BinaryIO,
    filename: str,
    max_size_bytes: int,
    chunk_size: int = 64 * 1024,
) -> tuple[bytes, str]:
    """Membaca stream file, memvalidasi ukuran, keutuhan, dan magic bytes (D-12).

    Mengembalikan (bytes_data, extension).
    """
    ext = validate_extension(filename)

    chunks = []
    total_bytes = 0

    while True:
        # UploadFile.read bisa berupa async atau sync tergantung konteks
        if hasattr(stream, "read"):
            chunk = stream.read(chunk_size)
            if hasattr(chunk, "__await__"):
                chunk = await chunk
        else:
            chunk = b""

        if not chunk:
            break

        total_bytes += len(chunk)
        if total_bytes > max_size_bytes:
            raise AppError(
                status_code=413,
                error="FILE_TOO_LARGE",
                message="Ukuran file melebihi batas maksimum.",
            )
        chunks.append(chunk)

    if total_bytes == 0:
        raise AppError(
            status_code=422,
            error="EMPTY_FILE",
            message="File kosong (0 byte).",
        )

    data = b"".join(chunks)

    # Validasi magic bytes untuk format biner (FR-26, AC-29, EC-2)
    expected_magic = MAGIC_BYTES.get(ext)
    if expected_magic:
        if not data.startswith(expected_magic):
            raise AppError(
                status_code=422,
                error="INVALID_FILE_CONTENT",
                message="Isi file tidak sesuai dengan format ekstensinya.",
            )

    # Pra-pindai arsip ZIP (NFR-S4, AC-14, AC-32, EC-18)
    if ext == ".zip":
        validate_zip_archive(data)

    return data, ext


def validate_zip_archive(data: bytes) -> None:
    """Pra-pindai isi file ZIP sebelum diteruskan ke konversi (NFR-S4, AC-14, AC-32)."""
    try:
        with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
            infolist = zf.infolist()

            # 1. Batas jumlah entri (AC-14)
            if len(infolist) > MAX_ZIP_ENTRIES:
                raise AppError(
                    status_code=422,
                    error="ARCHIVE_LIMIT_EXCEEDED",
                    message="Jumlah entri dalam file ZIP melebihi batas maksimum 100.",
                )

            total_uncompressed = 0
            for info in infolist:
                # Lewati direktori murni
                if info.is_dir() or info.filename.endswith("/"):
                    continue

                total_uncompressed += info.file_size
                if total_uncompressed > MAX_ZIP_UNCOMPRESSED_BYTES:
                    raise AppError(
                        status_code=422,
                        error="ARCHIVE_LIMIT_EXCEEDED",
                        message="Total ukuran ekstraksi ZIP melebihi batas 200 MB.",
                    )

                entry_ext = get_extension(info.filename)

                # 2. Tidak boleh ada ZIP bersarang (AC-32, EC-18)
                if entry_ext == ".zip":
                    raise AppError(
                        status_code=422,
                        error="ARCHIVE_CONTENT_NOT_ALLOWED",
                        message="File ZIP tidak boleh memuat arsip bersarang (nested ZIP).",
                    )

                # 3. Semua entri harus di allowlist (AC-32, EC-18)
                # Entri ZIP yang valid harus salah satu dari format allowlist non-zip
                valid_entry_exts = ALLOWED_EXTENSIONS - {".zip"}
                if not entry_ext or entry_ext not in valid_entry_exts:
                    raise AppError(
                        status_code=422,
                        error="ARCHIVE_CONTENT_NOT_ALLOWED",
                        message=f"ZIP memuat file terlarang atau tidak didukung: '{info.filename}'.",
                    )

    except zipfile.BadZipFile:
        raise AppError(
            status_code=422,
            error="INVALID_FILE_CONTENT",
            message="File ZIP rusak atau tidak valid.",
        )
