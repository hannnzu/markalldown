# Changelog

Format mengikuti [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Phase 2 — Konversi Satu File (2026-10-24)
- Berhasil implementasi endpoint `POST /api/convert/file`.
- Validasi file berlapis (D-12):
  - Ekstensi allowlist case-insensitive (FR-3, EC-19) -> 415 `UNSUPPORTED_FILE_TYPE`
  - File kosong 0 byte (EC-1) -> 422 `EMPTY_FILE`
  - Batas ukuran file via stream chunking (FR-4, AC-3) -> 413 `FILE_TOO_LARGE`
  - Magic bytes binary signature verification (FR-26, AC-29, EC-2) -> 422 `INVALID_FILE_CONTENT`
  - Pra-pindai arsip ZIP (NFR-S4, AC-14, AC-32, EC-18) -> 422 `ARCHIVE_*`
- Layanan konversi stream MarkItDown (FR-8, AC-24) dengan proteksi timeout 60 detik (NFR-R2, AC-15) dan konkurensi semaphore 3 (NFR-P3, D-9).
- Pemetaan error markitdown (EC-3: terenkripsi/rusak) ke 422 `CONVERSION_FAILED`.
- Deteksi output kosong (EC-4: PDF tanpa teks) mengembalikan 200 dengan `warnings: ["NO_TEXT_EXTRACTED"]`.
- Sanitasi nama file mencegah path traversal (EC-5).
- Seluruh 13 tes AC/EC Phase 2 hijau (100% lulus).

### Pengukuran & Benchmark (D-3, NFR-P2)
- Pengukuran performa konversi file ~5 MB (Target: p95 < 15.000 detik):
  - DOCX test document (~450k karakter): Median p50 = 0.909s, p95 = 1.398s
  - Markdown/Text document (4.78 MB, 85k item baris): Median p50 = 0.173s, p95 = 0.324s
- Kesimpulan: Performa konversi berada jauh di bawah ambang batas maksimum 15 detik (MEMENUHI NFR-P2).

### Phase 1 — Skeleton Backend (2026-10-24)
- FastAPI application setup dengan global `ApiError` handler (AC-23, NFR-R1).
- `GET /api/health` endpoint (AC-11, NFR-P1).
- CORS configuration dengan origin whitelist (AC-12, FR-14).
- SlowAPI rate limiter setup (AC-13, NFR-S2).

### Phase 0 — Bootstrap (2026-10-24)
- Inisialisasi Git repository & `.gitignore`.
- Pembuatan virtual environment Python 3.12 (`.venv`) dan instalasi semua dependensi runtime + dev.
- Eksekusi deterministik `scripts/make_fixtures.py` (22 fixtures lengkap).
- Baseline tes terverifikasi: 33 merah (NotImplementedError), 3 hijau (Phase 1).
