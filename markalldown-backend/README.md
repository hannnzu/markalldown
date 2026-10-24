# markalldown-backend

Backend FastAPI untuk **markalldown-web** — wrapper `markitdown` (Microsoft) yang mengekspos REST API untuk konversi file/URL ke Markdown.

## Stack

- **Python 3.12** + FastAPI + Uvicorn
- **markitdown** `>=0.1.5,<0.2` (pdf, docx, pptx, xlsx, xls, youtube-transcription)
- **Supabase** — rate limiting terpusat (multi-instance)
- Deploy: **Railway** atau **Render**

## Struktur

```
app/
  main.py          # FastAPI app, CORS, rate limit, error handlers
  config.py        # pydantic-settings: AppConfig
  routers/
    health.py      # GET /api/health
    convert.py     # POST /api/convert/file|files|url  (Phase 2+)
  services/
    converter.py   # markitdown wrapper: convert_stream, to_thread, semaphore(3)
    validators.py  # ekstensi allowlist, magic bytes, ukuran, ZIP scan
    url_fetcher.py # SSRF-safe httpx fetcher + YouTube detection
  models/
    schemas.py     # Pydantic: ApiError, ConvertFileResponse, BatchItem, ...
  utils/
    file_utils.py  # sanitasi nama file
tests/
  fixtures/        # Jalankan `python scripts/make_fixtures.py` sekali
  test_spec_001.py # 36 test (Phase 1: hijau; Phase 2–5: merah/NotImplementedError)
scripts/
  make_fixtures.py # Generator fixture deterministik
```

## Setup

```bash
# 1. Buat virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Copy env
cp .env.example .env
# Edit .env: isi SUPABASE_URL dan SUPABASE_SERVICE_ROLE_KEY

# 4. Buat fixtures (sekali)
python scripts/make_fixtures.py

# 5. Jalankan tests — Phase 1 harus hijau, sisanya merah
python -m pytest -q

# 6. Jalankan dev server
uvicorn app.main:app --reload --port 8000
```

## Phase status

| Phase | Fokus | Status |
|-------|-------|--------|
| 0 | Bootstrap | ✅ |
| 1 | Skeleton (health, CORS, error) | ✅ |
| 2 | Konversi satu file | 🔴 |
| 3 | ZIP hardening, timeout, rate limit | 🔴 |
| 4 | Batch | 🔴 |
| 5 | URL & YouTube | 🔴 |
| 9 | Docker & deploy Railway | 🔴 |

## Deploy (Railway)

Lihat `DEPLOYMENT.md`. Environment variables yang wajib di-set:

```
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-frontend.vercel.app
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=...
```
