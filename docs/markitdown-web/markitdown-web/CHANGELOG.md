# Changelog

Format mengikuti [Keep a Changelog](https://keepachangelog.com/). Catat juga versi terkunci dan hasil pengukuran di sini.

## [Unreleased]

### Persiapan (2026-10-24)
- Spec SPEC-001 ditulis dan divalidasi (100/100); 32 AC, 19 EC, 13 keputusan (D-1..D-13).
- Stub tes: 36 backend (pytest) + 15 frontend (vitest), semuanya merah.
- Fixture tes dibuat oleh `backend/scripts/make_fixtures.py` (22 file, termasuk kasus negatif).
- Diverifikasi di sandbox (markitdown 0.1.5, Python 3.12): 14 format FR-5 terkonversi lewat `convert_stream()`.
- Temuan yang mengubah spec: file palsu `.pdf` lolos sebagai teks (FR-26 ditambah); ZIP 101 entri, ZIP berisi `.exe`, dan ZIP bersarang lolos tanpa batas (NFR-S4 diperkuat, EC-18); PDF terenkripsi melempar `PDFPasswordIncorrect`; PDF tanpa teks menghasilkan string kosong.
- Belum diverifikasi: konversi URL/YouTube (tanpa jaringan), benchmark NFR-P2/NFR-R2, kompatibilitas versi FastAPI dkk.

### Versi terkunci
_(isi setelah suite hijau pertama: output `pip freeze`, versi Next.js, Tailwind, dll.)_

### Pengukuran
_(isi: benchmark Phase 2, uji manual URL/YouTube Phase 5, smoke test produksi Phase 9.)_
