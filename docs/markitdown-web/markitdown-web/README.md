# markitdown-web

Website untuk mengubah file dan URL menjadi Markdown, memakai library [markitdown](https://github.com/microsoft/markitdown) (Microsoft).

**Status:** persiapan selesai, implementasi belum dimulai. Spec: `specs/SPEC-001-markitdown-web.md` (skor validator 100/100).

## Fitur (MVP)

Unggah file lewat drag & drop (satu atau batch), konversi URL web dan YouTube, pratinjau split view (Markdown mentah dan hasil render), unduh `.md` per file atau ZIP, dark/light mode.

Format didukung (terverifikasi dengan markitdown 0.1.5): PDF, DOCX, PPTX, XLSX, XLS, CSV, HTML, HTM, JSON, XML, TXT, MD, EPUB, ZIP. Gambar, audio, `.doc`, `.ppt`, `.rst` tidak termasuk MVP (lihat Decisions D-1, D-2 di spec).

## Stack

Backend: Python 3.12, FastAPI, markitdown. Frontend: Next.js (App Router), TypeScript, Tailwind. Stateless: tanpa database.

## Struktur

```
specs/        SPEC-001 (kontrak, sumber kebenaran)
docs/         IMPLEMENTATION_PLAN.md, PROJECT_PLAN.md (rencana awal, sebagian usang)
backend/      requirements, pyproject, scripts/make_fixtures.py, tests/ (stub merah + fixture)
frontend/     tests/ (stub vitest), .env.local.example
AGENTS.md     instruksi untuk AI coding agent
API_SPEC.md   ringkasan kontrak API
DEPLOYMENT.md panduan deploy
```

## Mulai

Baca `AGENTS.md`, lalu ikuti `docs/IMPLEMENTATION_PLAN.md` mulai Phase 0.

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest -q        # baseline: 36 failed (sengaja merah)
```

## Lisensi

Belum ditentukan. markitdown berlisensi MIT (periksa repo aslinya).
