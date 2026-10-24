# Backend — FastAPI

Lihat `../AGENTS.md` untuk aturan kerja dan `../docs/IMPLEMENTATION_PLAN.md` (Phase 1–5).

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
python scripts/make_fixtures.py      # opsional; fixture sudah di tests/fixtures/
python -m pytest -q                  # baseline: 36 failed
uvicorn app.main:app --reload --port 8000
```

Fixture negatif: `empty.pdf` (EC-1), `fake.pdf` (EC-2, AC-29), `encrypted.pdf` (EC-3, password `rahasia`), `no_text.pdf` (EC-4), `malware.exe` (AC-2), `too_many_entries.zip` (AC-14), `zip_with_exe.zip` dan `nested.zip` (AC-32, EC-18).
