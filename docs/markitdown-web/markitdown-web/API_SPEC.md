# API Spec — markitdown-web

Ringkasan dari `specs/SPEC-001-markitdown-web.md` (bagian API Contracts). **Jika berbeda, spec menang.** Base path: `/api`. Semua error berbentuk `{ "error": "<KODE>", "message": "<pesan>" }`.

## Endpoint

| Method | Path | Fungsi |
|--------|------|--------|
| GET | `/api/health` | `{ "status": "ok", "version": "..." }` |
| POST | `/api/convert/file` | `multipart/form-data`, field `file` |
| POST | `/api/convert/files` | `multipart/form-data`, field `files` (1–20 file, total ≤ 100 MB) |
| POST | `/api/convert/url` | JSON `{ "url": "..." }` |

## Contoh

```bash
curl -F "file=@sample.pdf" http://localhost:8000/api/convert/file
curl -F "files=@a.pdf" -F "files=@b.pptx" http://localhost:8000/api/convert/files
curl -H "Content-Type: application/json" -d '{"url":"https://example.com"}' http://localhost:8000/api/convert/url
```

Respons `/convert/file` (200): `{ filename, markdown, size_bytes, converted_at, warnings[] }`.
Respons `/convert/files` (200): `{ results: [{ filename, markdown|null, status: "success"|"error", error?, message? }], total, success, failed }`.
Respons `/convert/url` (200): `{ source_url, markdown, converted_at }`.

## Kode error

| Kode | HTTP | Kapan |
|------|------|-------|
| UNSUPPORTED_FILE_TYPE | 415 | Ekstensi di luar allowlist (FR-3) |
| FILE_TOO_LARGE | 413 | > `MAX_FILE_SIZE_MB` (FR-4) |
| BATCH_TOO_LARGE | 413 | Total batch > `MAX_BATCH_SIZE_MB` (FR-27) |
| EMPTY_FILE | 422 | 0 byte (EC-1) |
| INVALID_FILE_CONTENT | 422 | Magic bytes tidak cocok (FR-26) |
| ARCHIVE_LIMIT_EXCEEDED | 422 | ZIP > 100 entri / > 200 MB terekstrak (NFR-S4) |
| ARCHIVE_CONTENT_NOT_ALLOWED | 422 | ZIP berisi entri terlarang atau ZIP bersarang |
| NO_FILES / TOO_MANY_FILES | 422 | Batch kosong / > 20 file |
| CONVERSION_FAILED | 422 | markitdown gagal (mis. PDF berpassword) |
| TRANSCRIPT_UNAVAILABLE | 422 | YouTube tanpa transkrip |
| URL_NOT_ALLOWED | 400 | Skema salah atau alamat non-publik (FR-11, FR-12) |
| RATE_LIMITED | 429 | > 30 request/menit/IP |
| URL_FETCH_FAILED | 502 | URL tidak terjangkau |
| UPSTREAM_THROTTLED | 503 | YouTube membatasi laju |
| CONVERSION_TIMEOUT | 504 | > 60 detik |
| INTERNAL_ERROR | 500 | Lainnya; tanpa detail internal (AC-23) |
