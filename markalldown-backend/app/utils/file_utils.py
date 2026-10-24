"""Sanitasi nama file — EC-5: path traversal prevention.

Aturan (SPEC-001 EC-5):
- Nama file dari pengguna TIDAK dipakai untuk penyimpanan (NFR-S3: UUID)
- Respons memakai nama yang sudah disanitasi (tanpa path component)
"""
from __future__ import annotations

import os
import unicodedata
import re


def sanitize_filename(filename: str) -> str:
    """Sanitasi nama file dari input pengguna.

    - Strip komponen path (basename only)
    - Hapus karakter tidak aman
    - Normalkan unicode
    - Fallback ke 'upload' jika kosong setelah sanitasi
    """
    # Ambil basename saja (hapus path traversal)
    name = os.path.basename(filename)

    # Normalkan unicode
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")

    # Hapus karakter yang tidak aman
    name = re.sub(r'[^\w.\-]', '_', name)

    # Hapus titik berulang (mencegah ../  dan semacamnya)
    name = re.sub(r'\.{2,}', '.', name)

    # Batasi panjang
    if len(name) > 255:
        stem, _, ext = name.rpartition(".")
        name = stem[:250] + ("." + ext if ext else "")

    return name or "upload"
