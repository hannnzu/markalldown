# Implementation Plan — markitdown-web

Turunan dari `specs/SPEC-001-markitdown-web.md`. Kerjakan berurutan. Tiap phase punya exit criteria; jangan lanjut sebelum terpenuhi.

**Baseline sebelum mulai:** backend `python -m pytest -q` → 36 failed; frontend `npx vitest run` → 15 failed (setelah vitest terpasang). Semua merah dengan sengaja.

Estimasi dari plan awal (11–19 jam) tidak diubah; belum ada data untuk merevisinya.

| Phase | Fokus | AC | EC |
|-------|-------|----|----|
| 0 | Bootstrap & verifikasi lingkungan | — | — |
| 1 | Skeleton backend | AC-11, 12, 23 | — |
| 2 | Konversi satu file + benchmark | AC-1, 2, 3, 5, 6, 24, 29 | EC-1, 2, 3, 4, 5, 19 |
| 3 | Hardening: ZIP, timeout, rate limit | AC-13, 14, 15, 32 | EC-14, 18 |
| 4 | Batch | AC-4, 31 | EC-6, 7, 8, 17 |
| 5 | URL & YouTube | AC-7, 8, 9, 10 | EC-9, 10, 11, 12 |
| 6 | Fondasi frontend | AC-21 | — |
| 7 | DropZone & antrean | AC-16, 17, 22, 25 | EC-13, 16 |
| 8 | URL input, pratinjau, unduhan | AC-18, 19, 20, 26, 27, 28, 30 | EC-15 |
| 9 | Docker & deploy manual | (NFR-S1, NFR-SC1) | — |

Total: 32 AC + 19 EC, semuanya terpetakan.

## Phase 0 — Bootstrap

1. `git init`; commit isi folder ini apa adanya (spec, stub tes, fixture, dokumen).
2. Backend venv + `pip install -r requirements-dev.txt`; `python -m pytest -q` harus menunjukkan 36 failed (bukan error import).
3. Jalankan `python scripts/make_fixtures.py`; `git status` harus bersih (fixture deterministik).

Exit: baseline merah terkonfirmasi.

## Phase 1 — Skeleton backend

Buat `app/main.py`, `config.py`, `routers/health.py`, `models/schemas.py`, handler error global.
- AC-11 health. AC-12 CORS (uji dengan `Origin` asing). AC-23 semua error → JSON `ApiError`, tanpa stack trace/path.

Exit: 3 AC hijau.

## Phase 2 — Konversi satu file

Buat `services/validators.py`, `services/converter.py`, `utils/file_utils.py`, `routers/convert.py` (`/file`).
Urutan validasi (D-12): ekstensi → file kosong (EC-1) → baca stream dengan batas ukuran (AC-3) → magic bytes (AC-29, EC-2) → `convert_stream(StreamInfo(extension, filename))` di `to_thread`.
- Petakan exception markitdown ke `CONVERSION_FAILED` (EC-3: `encrypted.pdf` melempar `PDFPasswordIncorrect`).
- String kosong dari konversi (EC-4: `no_text.pdf`) → 200 dengan `warnings: ["NO_TEXT_EXTRACTED"]`.
- AC-6 mengulang untuk 14 format `sample.*`. AC-24 = tes statis (grep/AST) bahwa tidak ada `.convert(` dengan input pengguna. AC-5 = direktori upload/temp bersih.
- Sanitasi nama file (EC-5) dan ekstensi case-insensitive (EC-19).

**Benchmark (D-3):** buat PDF/DOCX ±5 MB, ukur waktu konversi 20 kali, catat p95 di `CHANGELOG.md`. Jika > 15 dtk, laporkan; jangan ubah tes.

Exit: AC/EC phase ini hijau; hasil benchmark tercatat.

## Phase 3 — Hardening

- ZIP (NFR-S4): pra-pindai sebelum konversi: ≤ 100 entri, total ukuran terekstrak ≤ 200 MB, semua ekstensi entri di allowlist, tanpa ZIP bersarang → `ARCHIVE_LIMIT_EXCEEDED` (AC-14) / `ARCHIVE_CONTENT_NOT_ALLOWED` (AC-32, EC-18). Fixture: `too_many_entries.zip`, `zip_with_exe.zip`, `nested.zip`.
- Timeout 60 dtk → 504 `CONVERSION_TIMEOUT` (AC-15; uji dengan konversi yang di-patch agar lambat). Semaphore 3.
- Rate limit 30/menit/IP untuk `/api/convert/*` → 429 `RATE_LIMITED` (AC-13).
- EC-14: klien memutus koneksi → tidak ada sisa file, server tidak crash.

Exit: AC/EC phase ini hijau.

## Phase 4 — Batch

`POST /api/convert/files`: 1–20 file (EC-7, EC-8), total ≤ `MAX_BATCH_SIZE_MB` dicek sebelum memproses (AC-31, EC-17), satu file gagal tidak menggagalkan batch (AC-4), urutan hasil = urutan input, nama kembar diproses (EC-6), konkurensi maks 3.

Exit: AC/EC phase ini hijau.

## Phase 5 — URL & YouTube

`services/url_fetcher.py` sesuai D-10. Tes memakai `respx` + monkeypatch resolver DNS (tidak memanggil internet).
- AC-9, AC-10: tolak `127.0.0.1`, `169.254.169.254`, `10.x`, `file://`, `ftp://`. EC-10: redirect ke IP privat ditolak.
- AC-7: web biasa. AC-8: YouTube (mock library transkrip). EC-9 `URL_FETCH_FAILED` 502, EC-11 `TRANSCRIPT_UNAVAILABLE`, EC-12 `UPSTREAM_THROTTLED`.
- **Setelah hijau: uji manual satu kali** dengan URL nyata dan satu video YouTube di mesin berinternet; catat hasilnya di `CHANGELOG.md`.

Exit: AC/EC hijau + catatan uji manual.

## Phase 6 — Fondasi frontend

```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir
npm install react-dropzone axios zustand sonner react-markdown remark-gfm react-resizable-panels jszip
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom @vitejs/plugin-react
```
Kunci versi, catat di `CHANGELOG.md`. Salin `.env.local.example` → `.env.local`. Siapkan `layout.tsx`, `globals.css` (variabel warna terang/gelap), `ThemeToggle`, `services/api.ts`, `types/index.ts`.
- AC-21: tema default mengikuti sistem; toggle mengubah.
- Pastikan `tests/spec-001.test.ts` ikut terbaca vitest.

Exit: AC-21 hijau; `npm run lint` bersih.

## Phase 7 — DropZone & antrean

`DropZone` (AC-25 `data-dragging`, AC-22 keyboard Enter), validasi klien (AC-16), `convertStore`, `FileQueue` status per file + progres unggah (AC-17, D-7). EC-13 backend mati → toast + item `error` bisa dicoba ulang. EC-16 file sama dua kali → dua item.

Exit: AC/EC phase ini hijau.

## Phase 8 — URL input, pratinjau, unduhan

`UrlInput` (AC-26), `MarkdownPreview` (AC-18; panel resizable AC-27; **tanpa raw HTML**, AC-30; EC-15 hasil > 5 MB dipotong saat render), `DownloadButton` (AC-19 nama `.md`; AC-20 ZIP via `jszip` hanya hasil sukses), toast error per file (AC-28).

Exit: seluruh suite frontend hijau.

## Phase 9 — Docker & deploy manual

Dockerfile backend (Python 3.12 slim, user non-root, tanpa ffmpeg) dan frontend (Next standalone), `docker-compose.yml` untuk lokal dengan `NEXT_PUBLIC_API_URL=http://localhost:8000`. Ikuti `DEPLOYMENT.md`. CI/CD otomatis di luar scope (OS-9). Verifikasi NFR-S1 (HTTPS) di URL produksi dan CORS (AC-12) terhadap domain produksi.

Exit: aplikasi berjalan di produksi, smoke test manual: unggah satu PDF dan satu URL.

## Self-review akhir

- [ ] 32 AC dan 19 EC punya tes hijau (36 backend + 15 frontend).
- [ ] Tidak ada item OS-1..OS-10 yang terbangun.
- [ ] API di kode = `API_SPEC.md`; model = bagian Data Models spec.
- [ ] NFR terukur: P1/P2 (benchmark), S2, S4, R2 punya bukti.
- [ ] Catatan uji manual URL/YouTube dan benchmark ada di `CHANGELOG.md`.
