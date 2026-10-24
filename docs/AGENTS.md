# AGENTS.md — markitdown-web

Instruksi untuk AI coding agent (Cursor, Antigravity, Copilot, Claude Code, Codex, dll). Baca seluruh file ini sebelum mengubah apa pun. Jika IDE kamu memakai nama file aturan lain, salin isi file ini ke sana.

## Apa proyek ini

Website converter file/URL ke Markdown. Backend FastAPI membungkus library `markitdown` (Microsoft); frontend Next.js (App Router, TypeScript, Tailwind). **Stateless**: tanpa database, tanpa akun, tanpa penyimpanan hasil di server. UI berbahasa Indonesia.

## Sumber kebenaran (urutan prioritas)

1. `specs/SPEC-001-markitdown-web.md` — kontrak. Setiap baris kode harus bisa ditelusuri ke FR/NFR/AC/EC di sini. **Bagian Decisions (D-1..D-13) mengikat.**
2. `docs/IMPLEMENTATION_PLAN.md` — urutan kerja per phase dan pemetaan ke AC/EC.
3. `API_SPEC.md` — ringkasan kontrak API (turunan spec; jika beda, spec menang).
4. `docs/PROJECT_PLAN.md` — rencana awal, **sebagian usang**. Jika bertentangan dengan spec, abaikan.

## Aturan kerja (spec-driven + TDD)

- **Tidak ada fitur di luar spec.** Jika sesuatu dibutuhkan tapi tidak ada di spec, **berhenti dan tanya** (format di bawah). Jangan menebak. Cek juga daftar Out of Scope (OS-1..OS-10); jangan membangunnya.
- Kerjakan **satu phase, satu acceptance criterion** sekali jalan, urut seperti `docs/IMPLEMENTATION_PLAN.md`.
- Siklus: ubah stub tes untuk AC/EC itu menjadi tes nyata (merah karena perilaku belum ada, bukan karena `NotImplementedError`) → tulis kode minimal sampai hijau → jalankan seluruh suite → commit. Satu commit per AC/kelompok EC kecil.
- **Jangan melonggarkan atau menghapus tes agar lulus.** Jika angka di spec ternyata tidak realistis (mis. NFR-P2, NFR-R2), laporkan dengan data; yang direvisi adalah spec (D-3), atas persetujuan pemilik proyek.
- Stub tes: `backend/tests/test_spec_001.py` (pytest, 36 tes) dan `frontend/tests/spec-001.test.ts` (vitest, 15 tes). Semuanya awalnya merah (baseline). Nama tes memuat ID (`ac01`, `ec02`, ...).
- Jangan refactor besar sebelum seluruh AC hijau.

### Format eskalasi (kalau harus berhenti)

```
Blocked on: <ID, mis. FR-12>
Question: <pertanyaan spesifik yang bisa dijawab>
Options: A) ... (plus/minus)  B) ... (plus/minus)
Recommendation: <A atau B + alasan>
Impact of waiting: <apa yang tertahan>
```

## Perintah

```bash
# Backend (dari backend/)
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python scripts/make_fixtures.py                          # sekali; fixture sudah ada di repo
python -m pytest -q
uvicorn app.main:app --reload --port 8000

# Frontend (dari frontend/) — setelah create-next-app, lihat IMPLEMENTATION_PLAN Phase 6
npm run dev
npx vitest run
npm run lint
```

## Arsitektur backend (struktur target)

```
backend/app/
  main.py                 # FastAPI app, CORS, rate limit, exception handlers -> ApiError JSON
  config.py               # pydantic-settings: AppConfig (lihat spec "Data Models")
  routers/health.py       # GET /api/health
  routers/convert.py      # POST /api/convert/file | files | url
  services/converter.py   # pembungkus markitdown: convert_stream, to_thread, semaphore(3), wait_for(60s)
  services/validators.py  # ekstensi allowlist, magic bytes, ukuran stream, pra-pindai ZIP
  services/url_fetcher.py # fetch URL aman (SSRF) + deteksi YouTube
  models/schemas.py       # Pydantic: ApiError, ConvertFileResponse, BatchItem, ...
  utils/file_utils.py     # sanitasi nama file
```

Frontend (target, `src/`): `app/{layout,page}.tsx`, `components/{DropZone,UrlInput,FileQueue,MarkdownPreview,ProgressBar,ThemeToggle,DownloadButton}.tsx`, `hooks/useConvert.ts`, `store/convertStore.ts` (Zustand), `services/api.ts` (axios), `types/index.ts`.

## Aturan keamanan (tidak bisa ditawar)

1. **Jangan** panggil `MarkItDown.convert()` dengan path/URL dari pengguna. Pakai `convert_stream()` dengan `StreamInfo(extension=..., filename=...)` (FR-8). README markitdown sendiri memperingatkan agar tidak meneruskan input tak tepercaya langsung.
2. **Validasi berlapis sebelum konversi** (D-12): allowlist ekstensi (case-insensitive) → magic bytes (FR-26) → ukuran saat membaca per chunk (jangan percaya `Content-Length`) → untuk ZIP: pra-pindai jumlah entri, total ukuran, ekstensi entri, ZIP bersarang (NFR-S4).
3. **Fakta terverifikasi tentang markitdown 0.1.5** (kenapa langkah 2 wajib): file `.pdf` berisi teks biasa dikonversi diam-diam sebagai teks; ZIP 101 entri, ZIP berisi `.exe`, dan ZIP bersarang semuanya dikonversi tanpa batas; `.exe` menghasilkan karakter sampah; PDF terenkripsi melempar `PDFPasswordIncorrect`; PDF tanpa teks mengembalikan string kosong.
4. **URL (D-10):** web biasa diambil oleh fetcher kita sendiri (`httpx`): hanya http/https, resolve DNS lalu tolak IP privat/loopback/link-local, redirect manual maks 5 dengan validasi ulang tiap hop, timeout 15 dtk, batas 20 MB. YouTube hanya host `youtube.com`, `www.youtube.com`, `m.youtube.com`, `youtu.be`.
5. **Jangan** log isi file atau URL pengguna (NFR-S5). Error ke klien selalu JSON `ApiError`, tanpa stack trace atau path server (AC-23).
6. **Frontend:** render Markdown dengan `react-markdown` + `remark-gfm`; **jangan** tambahkan `rehype-raw` atau `dangerouslySetInnerHTML` (NFR-S7).
7. CORS hanya dari `ALLOWED_ORIGINS`; `*` dilarang di production.

## Keputusan stack yang sudah final

- Python 3.12; `markitdown[pdf,docx,pptx,xlsx,xls,youtube-transcription]>=0.1.5,<0.2` (bukan `[all]`). `aiofiles` tidak dipakai.
- markitdown sinkron → `asyncio.to_thread` + semaphore 3 + `asyncio.wait_for(60)` (D-9). Tidak menulis file permanen.
- Rate limit in-memory per instance (D-4), mis. `slowapi`.
- Frontend: `react-markdown`, `remark-gfm`, `react-resizable-panels`, `jszip`, `react-dropzone`, `axios`, `zustand`, `sonner`. **Bukan** `@uiw/react-md-editor` (D-8).
- ZIP batch dibuat di klien (D-6). Progres: unggah nyata via `onUploadProgress`, konversi indeterminate (D-7).
- Versi Next.js/Tailwind: cek rilis stabil terbaru saat instalasi, kunci, dan catat di `CHANGELOG.md` (D-11). Pakai `--src-dir`.

## Yang belum terverifikasi (jangan berasumsi)

- Konversi URL web dan YouTube belum diuji nyata (sandbox spec tanpa jaringan). Tulis tes dengan mock (`respx`), lalu uji manual sekali di mesin dengan internet. Transkrip YouTube dari IP datacenter sering diblokir; itu ditangani EC-12.
- Angka performa NFR-P2 (15 dtk) dan NFR-R2 (60 dtk) belum pernah diukur. Ukur di Phase 2 dengan file ±5 MB.
- Versi paket selain markitdown (FastAPI, dll.) belum diuji bersama; setelah suite hijau pertama kali, bekukan versi.

## Definition of Done (per phase dan akhir)

- Semua tes AC/EC milik phase hijau; tidak ada regresi; `ruff check` dan `npm run lint` bersih.
- Kontrak API di kode = `API_SPEC.md` (nama field, tipe, status code).
- Tidak ada fitur di luar spec; tidak ada item Out of Scope yang terbangun.
- `CHANGELOG.md` diperbarui; versi terkunci dicatat.
