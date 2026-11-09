# Changelog

Format mengikuti [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Phase 10 — Frontend: Build, TypeScript, & Dev Server (2026-10-25)
- TypeScript strict check: **0 error** pada seluruh codebase frontend.
- Dev server berjalan di `http://localhost:3000` (Next.js 16 + Turbopack).
- Verifikasi visual: header, DropZone, URL input, dan dark mode berfungsi tanpa console error.
- Downgrade `react-resizable-panels` → v2.1.9 (PanelGroup/PanelResizeHandle API).

### Phase 9 — Frontend: Global CSS Design System (2026-10-25)
- Design system lengkap dengan CSS custom properties (light + dark tokens) — NFR-A2 (WCAG 2.1 AA).
- Dark mode dengan no-flash inline script di root layout — FR-23, AC-21.
- Komponen: DropZone, URL Input, QueueItemCard, QueueList, SplitView, Toast, ThemeToggle.
- Animasi: indeterminate progress bar untuk status converting, toast fade-in, hover effects.
- Responsive: mobile-first layout dengan media query `@media (max-width: 640px)`.

### Phase 8 — Frontend: Komponen & Store (2026-10-25)
- `src/types/api.ts` — TypeScript interfaces (ApiError, ConvertFileResponse, dll.) sesuai SPEC-001.
- `src/types/queue.ts` — QueueItem data model sesuai SPEC-001 § Data Models.
- `src/services/api.ts` — Axios wrapper dengan `onUploadProgress` per D-7.
- `src/store/queue.ts` — Zustand store untuk antrian konversi per SPEC-001 QueueItem.
- `src/hooks/useTheme.ts` — Dark/light mode hook dengan system preference sebagai default (FR-23, AC-21).
- `src/components/DropZone.tsx` — Drag & drop, validasi client-side, keyboard accessible (FR-15, AC-16, AC-22, AC-25).
- `src/components/UrlInput.tsx` — Input URL dengan validasi http/https (FR-18, AC-26).
- `src/components/QueueItemCard.tsx` — Item antrean dengan progress bar dan aria-live (FR-17, AC-17, NFR-A3).
- `src/components/QueueList.tsx` — List antrean + ZIP client-side via JSZip (FR-22, AC-20, D-6).
- `src/components/SplitView.tsx` — Resizable split view (FR-19, FR-20, AC-27) — XSS safe, no rehype-raw (NFR-S7, AC-30).
- `src/components/Toast.tsx` — Toast notifikasi dengan aria-live (FR-25, AC-28, NFR-A3).
- `src/components/ThemeToggle.tsx` — Toggle mode tema (FR-23).
- `src/app/page.tsx` — Halaman utama: orchestrate konversi file/batch/URL dengan error handling.
- `src/app/layout.tsx` — Root layout dengan metadata SEO dan no-flash dark mode script.

### Phase 7 — Frontend: Next.js Scaffold (2026-10-25)
- Scaffold `create-next-app@latest` dengan TypeScript, App Router, src-dir, ESLint.
- Install library: `axios`, `jszip`, `react-markdown`, `remark-gfm`, `react-resizable-panels@2`, `zustand`.
- Next.js 16.4.3 (Turbopack), dikunci di CHANGELOG sesuai D-11.

### Phase 6 — Backend: URL & YouTube (selesai verifikasi) (2026-10-25)
- Verifikasi akhir: **36 tests passed** (31.21s), 0 failures.

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
