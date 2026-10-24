# Spec: markitdown-web

**Author:** [isi nama kamu]
**Date:** 2026-10-24
**Status:** Approved (menunggu konfirmasi author atas Decisions D-1 s/d D-13 di bagian akhir)
**Reviewers:** [isi reviewer / dosen / rekan tim]
**Related specs:** None (spec pertama). Sumber: `markitdown-web-project-plan.md`

---

## Context

`markitdown` (Microsoft) adalah library Python yang mengubah banyak format file menjadi Markdown, tetapi hanya bisa dipakai lewat CLI atau kode Python. Orang yang tidak nyaman dengan terminal tidak punya cara mudah memakainya, dan tidak ada antarmuka untuk melihat hasilnya langsung atau mengonversi banyak file sekaligus.

`markitdown-web` adalah website sederhana: pengguna mengunggah file atau memasukkan URL, lalu mendapat Markdown yang bisa dipratinjau dan diunduh. Backend FastAPI membungkus library `markitdown`; frontend Next.js menangani unggah, antrean, pratinjau, dan unduhan. Sistem ini **stateless**: tidak ada akun, tidak ada database, tidak ada penyimpanan hasil di server.

Belum ada metrik pengguna. Spec ini bertujuan sebagai kontrak implementasi untuk MVP (project belajar/demo), bukan produk berskala besar. Keputusan desain yang diambil, beserta bukti verifikasinya, ada di bagian **Decisions** di akhir dokumen.

---

## Functional Requirements

### Konversi file

- FR-1: The system MUST menerima satu file lewat `POST /api/convert/file` dan mengembalikan hasil konversi Markdown.
- FR-2: The system MUST menerima beberapa file lewat `POST /api/convert/files` dan mengembalikan hasil per file, dengan status `success` atau `error` untuk masing-masing.
- FR-3: The system MUST menolak file yang ekstensinya tidak ada di allowlist dengan HTTP 415.
- FR-4: The system MUST menolak file yang ukurannya melebihi `MAX_FILE_SIZE_MB` (default 50) dengan HTTP 413.
- FR-5: The system MUST mengonversi format berikut: PDF, DOCX, PPTX, XLSX, XLS, CSV, HTML, HTM, JSON, XML, TXT, MD, EPUB, ZIP.
- FR-6: The system MUST NOT gagal seluruh request batch karena satu file gagal; file lain tetap diproses.
- FR-7: The system MUST menghapus file sementara di server setelah konversi selesai, baik berhasil maupun gagal.
- FR-8: The system MUST memakai `convert_stream()` atau `convert_local()` dari markitdown dan MUST NOT memakai `convert()` dengan input yang dikontrol pengguna.
- FR-26: The system MUST memverifikasi signature (magic bytes) untuk format biner dan menolak file yang tidak cocok dengan HTTP 422 `INVALID_FILE_CONTENT`: PDF diawali `%PDF-`; DOCX, PPTX, XLSX, EPUB, ZIP diawali `PK\x03\x04`; XLS diawali `D0 CF 11 E0`.
- FR-27: The system MUST menolak request batch yang total ukuran filenya melebihi `MAX_BATCH_SIZE_MB` (default 100) dengan HTTP 413 `BATCH_TOO_LARGE`.

### Konversi URL

- FR-9: The system MUST menerima URL lewat `POST /api/convert/url` dan mengembalikan Markdown dari halaman web tersebut.
- FR-10: The system MUST mendukung URL YouTube dan mengembalikan transkrip jika tersedia.
- FR-11: The system MUST hanya menerima skema `http` dan `https`.
- FR-12: The system MUST NOT mengambil URL yang resolve ke alamat privat, loopback, atau link-local (perlindungan SSRF).

### API umum

- FR-13: The system MUST menyediakan `GET /api/health` yang mengembalikan status layanan.
- FR-14: The system MUST hanya mengizinkan CORS dari origin yang terdaftar di `ALLOWED_ORIGINS`.

### Frontend

- FR-15: The frontend MUST menyediakan area drag & drop dan tombol pilih file, dengan perubahan visual saat file sedang diseret di atasnya.
- FR-16: The frontend MUST memvalidasi ekstensi dan ukuran file di sisi klien sebelum mengirim ke backend.
- FR-17: The frontend MUST menampilkan antrean file dengan status per file: `pending`, `converting`, `success`, `error`.
- FR-18: The frontend MUST menyediakan input URL untuk konversi web dan YouTube.
- FR-19: The frontend MUST menampilkan pratinjau split view: sisi kiri Markdown mentah, sisi kanan hasil render.
- FR-20: The frontend SHOULD menyediakan pembatas split view yang bisa digeser (resizable).
- FR-21: The frontend MUST menyediakan unduhan `.md` per file, dengan nama file asli diganti ekstensinya menjadi `.md`.
- FR-22: The frontend MUST menyediakan unduhan semua hasil sukses sebagai satu ZIP pada mode batch.
- FR-23: The frontend MUST menyediakan toggle dark/light mode dan MUST mengikuti preferensi sistem sebagai default.
- FR-24: The frontend MUST menampilkan indikator progres unggah dan konversi per file.
- FR-25: The frontend MUST menampilkan pesan error yang spesifik per file yang gagal lewat toast.

---

## Non-Functional Requirements

### Performance

- NFR-P1: `GET /api/health` MUST merespons dalam < 200 ms (p95) pada kondisi normal.
- NFR-P2: Konversi file PDF/DOCX ≤ 5 MB SHOULD selesai dalam < 15 detik (p95). Angka ini **usulan** dan harus diukur (lihat D-3).
- NFR-P3: Batch SHOULD memproses file dengan konkurensi maksimum 3 per request agar memori tetap terkendali.

### Security

- NFR-S1: Semua trafik produksi MUST memakai HTTPS (TLS 1.2+).
- NFR-S2: Backend MUST membatasi laju request: maksimum 30 request per menit per IP untuk `/api/convert/*` (usulan, lihat D-4), dan mengembalikan HTTP 429 saat terlampaui.
- NFR-S3: File upload MUST disimpan hanya di direktori temp terisolasi dengan nama acak (UUID), bukan nama dari pengguna.
- NFR-S4: Konversi ZIP MUST dibatasi: maksimum 100 entri dan total ukuran terekstrak 200 MB, untuk mencegah zip bomb. Pemeriksaan MUST dilakukan sebelum konversi dimulai, dan ZIP yang berisi entri dengan ekstensi di luar allowlist atau berisi ZIP bersarang MUST ditolak. (markitdown sendiri tidak membatasi hal ini; terverifikasi, lihat D-2.)
- NFR-S5: Backend MUST NOT menulis isi file atau URL pengguna ke log.
- NFR-S6: Request ke URL eksternal MUST memakai timeout 15 detik dan batas ukuran respons 20 MB.
- NFR-S7: Pratinjau Markdown di frontend MUST NOT merender HTML mentah dari Markdown hasil konversi; tidak boleh ada elemen `<script>`, atribut `on*`, atau `javascript:` URL di DOM pratinjau. (Markdown berasal dari file/halaman web yang tidak tepercaya; hasil konversi pptx bahkan memuat komentar HTML.)

### Accessibility

- NFR-A1: Area upload MUST bisa dioperasikan dengan keyboard (Tab, Enter, Space).
- NFR-A2: Kontras teks MUST memenuhi WCAG 2.1 AA (4.5:1) di mode terang dan gelap.
- NFR-A3: Perubahan status konversi dan pesan error MUST diumumkan lewat `aria-live`.

### Scalability

- NFR-SC1: Backend MUST berjalan stateless sehingga bisa dijalankan lebih dari satu instance tanpa berbagi penyimpanan.

### Reliability

- NFR-R1: Backend MUST mengembalikan JSON error terstruktur (bukan stack trace) untuk semua kegagalan.
- NFR-R2: Backend MUST mengembalikan HTTP 504 jika satu konversi melebihi 60 detik (usulan, lihat D-3).

---

## Acceptance Criteria

### AC-1: Konversi satu file berhasil (FR-1, FR-5)
Given sebuah file `document.pdf` valid berukuran 1 MB
When klien mengirim `POST /api/convert/file` dengan file tersebut
Then respons berstatus 200
And body memuat `filename` = `document.pdf`, `markdown` tidak kosong, `size_bytes` = 1048576 (ukuran asli), dan `converted_at` format ISO 8601

### AC-2: Ekstensi tidak didukung ditolak (FR-3)
Given file `malware.exe`
When klien mengirim `POST /api/convert/file`
Then respons berstatus 415
And body memuat `error` = `UNSUPPORTED_FILE_TYPE`

### AC-3: File terlalu besar ditolak (FR-4)
Given `MAX_FILE_SIZE_MB` = 50 dan sebuah file 51 MB
When klien mengirim `POST /api/convert/file`
Then respons berstatus 413
And body memuat `error` = `FILE_TOO_LARGE`

### AC-4: Batch dengan campuran sukses dan gagal (FR-2, FR-6)
Given tiga file: `doc1.pdf` valid, `doc2.pptx` valid, dan `broken.pdf` korup
When klien mengirim `POST /api/convert/files`
Then respons berstatus 200
And `total` = 3, `success` = 2, `failed` = 1
And entri `broken.pdf` memiliki `status` = `error` dan `markdown` = null

### AC-5: File sementara dibersihkan (FR-7)
Given sebuah file valid dan sebuah file korup dikirim bergantian
When kedua konversi selesai
Then direktori upload temp tidak berisi file milik kedua request tersebut

### AC-6: Format inti terkonversi (FR-5)
Given satu contoh file valid untuk masing-masing format di FR-5
When tiap file dikirim ke `POST /api/convert/file`
Then tiap respons berstatus 200 dan `markdown` tidak kosong

### AC-7: Konversi URL web berhasil (FR-9, FR-11)
Given URL `https://example.com`
When klien mengirim `POST /api/convert/url` dengan URL tersebut
Then respons berstatus 200
And `source_url` = URL yang dikirim dan `markdown` tidak kosong

### AC-8: Konversi YouTube berhasil (FR-10)
Given URL video YouTube publik yang memiliki transkrip
When klien mengirim `POST /api/convert/url`
Then respons berstatus 200
And `markdown` memuat teks transkrip

### AC-9: URL internal ditolak (FR-12)
Given URL `http://127.0.0.1:8000/api/health`, `http://169.254.169.254/`, dan `http://10.0.0.5/`
When masing-masing dikirim ke `POST /api/convert/url`
Then masing-masing respons berstatus 400
And `error` = `URL_NOT_ALLOWED`

### AC-10: Skema selain http/https ditolak (FR-11)
Given URL `file:///etc/passwd` dan `ftp://example.com/a.txt`
When masing-masing dikirim ke `POST /api/convert/url`
Then masing-masing respons berstatus 400
And `error` = `URL_NOT_ALLOWED`

### AC-11: Health check (FR-13, NFR-P1)
Given backend berjalan
When klien memanggil `GET /api/health`
Then respons berstatus 200 dan `status` = `ok`

### AC-12: CORS membatasi origin (FR-14)
Given `ALLOWED_ORIGINS` = `http://localhost:3000`
When request datang dengan header `Origin: https://evil.example`
Then respons tidak memuat header `Access-Control-Allow-Origin` untuk origin tersebut

### AC-13: Rate limit (NFR-S2)
Given satu IP telah mengirim 30 request ke `/api/convert/file` dalam 1 menit
When IP yang sama mengirim request ke-31 dalam menit yang sama
Then respons berstatus 429
And `error` = `RATE_LIMITED`

### AC-14: Zip bomb ditolak (NFR-S4)
Given sebuah ZIP dengan 101 entri
When dikirim ke `POST /api/convert/file`
Then respons berstatus 422
And `error` = `ARCHIVE_LIMIT_EXCEEDED`

### AC-15: Timeout konversi (NFR-R2)
Given konversi yang berjalan lebih dari 60 detik
When batas waktu terlampaui
Then respons berstatus 504
And `error` = `CONVERSION_TIMEOUT`
And file sementara dihapus

### AC-16: Validasi klien sebelum upload (FR-16)
Given pengguna menjatuhkan `photo.exe` dan file 60 MB ke DropZone
When validasi klien berjalan
Then tidak ada request jaringan dikirim untuk kedua file
And toast error ditampilkan untuk masing-masing file

### AC-17: Antrean menampilkan status per file (FR-17, FR-24)
Given pengguna menambahkan tiga file valid ke antrean
When konversi berjalan
Then tiap item menampilkan status `pending`, lalu `converting`, lalu `success` atau `error`
And tiap item memiliki progress bar sendiri

### AC-18: Split view (FR-19)
Given sebuah hasil konversi sukses dipilih dari antrean
When pratinjau dibuka
Then panel kiri menampilkan Markdown mentah
And panel kanan menampilkan HTML hasil render dari Markdown yang sama

### AC-19: Unduh .md (FR-21)
Given hasil sukses untuk file `laporan.docx`
When pengguna menekan tombol unduh
Then browser mengunduh file bernama `laporan.md` berisi Markdown hasil konversi

### AC-20: Unduh ZIP batch (FR-22)
Given batch dengan 2 hasil sukses dan 1 hasil error
When pengguna menekan "Unduh semua"
Then browser mengunduh satu ZIP berisi tepat 2 file `.md`

### AC-21: Tema default mengikuti sistem (FR-23)
Given pengguna belum pernah memilih tema dan sistem operasi memakai mode gelap
When halaman dimuat pertama kali
Then halaman tampil di mode gelap
And toggle tema mengubah ke mode terang saat ditekan

### AC-22: Upload bisa dioperasikan keyboard (NFR-A1)
Given fokus berada di area DropZone
When pengguna menekan Enter
Then dialog pemilih file terbuka

### AC-23: Error tidak membocorkan detail internal (NFR-R1)
Given konversi gagal karena exception internal
When respons dikembalikan
Then body berformat JSON dengan `error` dan `message`
And body tidak memuat stack trace maupun path file server

### AC-24: Konversi tidak memakai convert() dengan input pengguna (FR-8)
Given kode layanan konverter di backend
When pengujian statis (grep/AST) dijalankan terhadap `app/services/converter.py`
Then tidak ada pemanggilan `MarkItDown.convert(` dengan path atau URL yang berasal dari request
And konversi file memakai `convert_stream(` atau `convert_local(`

### AC-25: Visual drag & drop (FR-15)
Given halaman utama terbuka
When pengguna menyeret sebuah file di atas DropZone
Then DropZone mendapat state visual "aktif" (atribut `data-dragging="true"`)
And state tersebut hilang saat file dijatuhkan atau meninggalkan area

### AC-26: Input URL di frontend (FR-18)
Given pengguna memasukkan URL YouTube valid ke UrlInput
When pengguna menekan tombol konversi
Then frontend mengirim `POST /api/convert/url` dengan body `{ "url": <nilai input> }`
And sebuah item bertipe `url` muncul di antrean

### AC-27: Split view bisa diubah ukurannya (FR-20)
Given split view terbuka dengan lebar panel kiri 50%
When pengguna menyeret pembatas ke kanan
Then lebar panel kiri bertambah dan lebar panel kanan berkurang
And lebar total kedua panel tetap 100%

### AC-28: Pesan error spesifik per file (FR-25)
Given batch dengan satu file yang gagal dengan `error` = `CONVERSION_FAILED`
When respons diterima
Then sebuah toast ditampilkan yang memuat nama file yang gagal
And pesan toast sama dengan `message` dari backend

### AC-29: Isi file tidak cocok dengan ekstensi (FR-26)
Given file `fake.pdf` yang berisi teks biasa (bukan PDF)
When klien mengirim `POST /api/convert/file`
Then respons berstatus 422
And body memuat `error` = `INVALID_FILE_CONTENT`

### AC-30: Pratinjau tidak merender HTML berbahaya (NFR-S7)
Given Markdown berisi `<script>alert(1)</script>` dan `<img src=x onerror=alert(1)>`
When Markdown tersebut dirender di panel pratinjau
Then DOM panel tidak memuat elemen `script` maupun atribut `onerror`
And teks tag tersebut tidak dieksekusi sebagai HTML

### AC-31: Batch melebihi total ukuran (FR-27)
Given `MAX_BATCH_SIZE_MB` = 100 dan tiga file masing-masing 40 MB
When klien mengirim `POST /api/convert/files`
Then respons berstatus 413
And body memuat `error` = `BATCH_TOO_LARGE`

### AC-32: ZIP berisi file di luar allowlist ditolak (NFR-S4)
Given ZIP yang berisi `evil.exe` dan ZIP lain yang berisi ZIP bersarang
When masing-masing dikirim ke `POST /api/convert/file`
Then masing-masing respons berstatus 422
And `error` = `ARCHIVE_CONTENT_NOT_ALLOWED`

---

## Edge Cases

- EC-1: File kosong (0 byte) -> HTTP 422 `EMPTY_FILE`.
- EC-2: Ekstensi benar tetapi isi bukan format tersebut (mis. `.pdf` berisi teks biasa) -> HTTP 422 `INVALID_FILE_CONTENT`. Pemeriksaan ini wajib ada di lapisan kita: markitdown diam-diam memperlakukan `fake.pdf` sebagai teks biasa dan mengembalikan hasil seolah sukses (terverifikasi, D-2).
- EC-3: PDF terenkripsi/berpassword -> `CONVERSION_FAILED` dengan pesan yang menyebut file terproteksi.
- EC-4: PDF hasil scan tanpa lapisan teks -> HTTP 200 dengan `markdown` kosong dan `warnings` berisi `NO_TEXT_EXTRACTED` (OCR di luar scope).
- EC-5: Nama file mengandung path traversal (`../../etc/passwd.pdf`) -> nama diabaikan untuk penyimpanan, respons memakai nama yang sudah disanitasi.
- EC-6: Dua file dengan nama sama dalam satu batch -> keduanya diproses; saat ZIP, nama kedua diberi akhiran `-1`.
- EC-7: Request batch tanpa file -> HTTP 422 `NO_FILES`.
- EC-8: Batch melebihi 20 file -> HTTP 422 `TOO_MANY_FILES` (batas 20, lihat D-5).
- EC-9: URL tidak bisa dijangkau (DNS gagal, timeout, 5xx) -> HTTP 502 `URL_FETCH_FAILED`.
- EC-10: URL redirect ke alamat privat -> ditolak `URL_NOT_ALLOWED` (validasi dilakukan pada setiap hop redirect).
- EC-11: Video YouTube tanpa transkrip atau privat -> HTTP 422 `TRANSCRIPT_UNAVAILABLE`.
- EC-12: YouTube membatasi laju (throttle) -> HTTP 503 `UPSTREAM_THROTTLED`.
- EC-13: Backend tidak bisa dijangkau dari frontend -> toast "Server tidak dapat dihubungi" dan item antrean ditandai `error`, bisa dicoba ulang.
- EC-14: Pengguna menutup tab saat konversi berjalan -> server menyelesaikan atau membatalkan konversi dan tetap menghapus file temp.
- EC-15: Markdown hasil sangat besar (> 5 MB) -> pratinjau tetap responsif dengan memotong render dan menampilkan peringatan; unduhan tetap menyertakan isi penuh.
- EC-16: Unggah file yang sama dua kali -> dua item antrean terpisah, tidak ada deduplikasi.
- EC-17: Total ukuran batch > `MAX_BATCH_SIZE_MB` -> HTTP 413 `BATCH_TOO_LARGE` sebelum file apa pun diproses.
- EC-18: ZIP berisi entri berekstensi di luar allowlist atau ZIP bersarang -> HTTP 422 `ARCHIVE_CONTENT_NOT_ALLOWED`.
- EC-19: File berekstensi huruf besar atau campuran (`REPORT.PDF`) -> diperlakukan sama dengan huruf kecil.

---

## API Contracts

Base path: `/api`. Semua error memakai bentuk `ApiError`.

```typescript
interface ApiError {
  error: string;       // kode mesin, mis. "FILE_TOO_LARGE"
  message: string;     // pesan untuk manusia, tanpa detail internal
}

type ErrorCode =
  | "UNSUPPORTED_FILE_TYPE"  // 415
  | "FILE_TOO_LARGE"         // 413
  | "EMPTY_FILE"             // 422
  | "INVALID_FILE_CONTENT"   // 422
  | "ARCHIVE_CONTENT_NOT_ALLOWED" // 422
  | "BATCH_TOO_LARGE"        // 413
  | "NO_FILES"               // 422
  | "TOO_MANY_FILES"         // 422
  | "ARCHIVE_LIMIT_EXCEEDED" // 422
  | "TRANSCRIPT_UNAVAILABLE" // 422
  | "URL_NOT_ALLOWED"        // 400
  | "RATE_LIMITED"           // 429
  | "URL_FETCH_FAILED"       // 502
  | "UPSTREAM_THROTTLED"     // 503
  | "CONVERSION_TIMEOUT"     // 504
  | "CONVERSION_FAILED"      // 422 (single) / status "error" (batch)
  | "INTERNAL_ERROR";        // 500
```

### GET /api/health

Success Response (200):
```typescript
interface HealthResponse {
  status: "ok";
  version: string;
}
```

### POST /api/convert/file

Request: `multipart/form-data`
```typescript
interface ConvertFileRequest {
  file: File;   // satu file, <= MAX_FILE_SIZE_MB, ekstensi di allowlist
}
```

Success Response (200):
```typescript
interface ConvertFileResponse {
  filename: string;       // nama tersanitasi
  markdown: string;
  size_bytes: number;     // ukuran file asli
  converted_at: string;   // ISO 8601 UTC
  warnings: string[];     // mis. ["NO_TEXT_EXTRACTED"]
}
```

Error Response (413 / 415 / 422 / 429 / 500 / 504): `ApiError`

### POST /api/convert/files

Request: `multipart/form-data`
```typescript
interface ConvertFilesRequest {
  files: File[];   // 1..20 file
}
```

Success Response (200):
```typescript
interface BatchItem {
  filename: string;
  markdown: string | null;
  status: "success" | "error";
  error?: string;          // ErrorCode, hanya jika status = "error"
  message?: string;
}

interface ConvertFilesResponse {
  results: BatchItem[];    // urutan sama dengan urutan input
  total: number;
  success: number;
  failed: number;
}
```

Error Response (413 / 422 / 429 / 500): `ApiError` (hanya untuk kegagalan level request, mis. `NO_FILES`)

### POST /api/convert/url

Request:
```typescript
interface ConvertUrlRequest {
  url: string;   // http(s), maksimum 2048 karakter
}
```

Success Response (200):
```typescript
interface ConvertUrlResponse {
  source_url: string;
  markdown: string;
  converted_at: string;   // ISO 8601 UTC
}
```

Error Response (400 / 422 / 429 / 502 / 503 / 504): `ApiError`

---

## Data Models

Sistem tidak memakai database. Model berikut adalah bentuk data di memori (backend config dan state frontend).

### AppConfig (backend, dari environment)
| Field | Type | Constraints |
|-------|------|-------------|
| ENVIRONMENT | enum | `development` atau `production` |
| ALLOWED_ORIGINS | string[] | Dipisah koma, tidak boleh `*` di production |
| MAX_FILE_SIZE_MB | integer | Default 50, minimum 1 |
| MAX_BATCH_SIZE_MB | integer | Default 100, minimum MAX_FILE_SIZE_MB |
| UPLOAD_DIR | string | Direktori temp, dapat ditulis |
| RATE_LIMIT_PER_MIN | integer | Default 30 |

### ConversionResult (backend, response)
| Field | Type | Constraints |
|-------|------|-------------|
| filename | string | Tersanitasi, tanpa path |
| markdown | string \| null | Null jika status error |
| size_bytes | integer | >= 1 |
| converted_at | string | ISO 8601 UTC, immutable |
| warnings | string[] | Dapat kosong |

### QueueItem (frontend, Zustand store)
| Field | Type | Constraints |
|-------|------|-------------|
| id | string | UUID, dibuat di klien |
| kind | enum | `file` atau `url` |
| name | string | Nama file atau URL |
| sizeBytes | number \| null | Null untuk URL |
| status | enum | `pending`, `converting`, `success`, `error` |
| progress | number | 0 sampai 100 |
| markdown | string \| null | Terisi saat `success` |
| errorCode | string \| null | Terisi saat `error` |

### ThemePreference (frontend)
| Field | Type | Constraints |
|-------|------|-------------|
| mode | enum | `system` (default), `light`, `dark` |

---

## Out of Scope

- OS-1: Akun pengguna, login, dan riwayat konversi — aplikasi stateless dan tidak menyimpan data pengguna.
- OS-2: Penyimpanan hasil konversi di server — privasi dan menghindari biaya storage.
- OS-3: OCR untuk PDF hasil scan dan deskripsi gambar berbasis LLM — butuh layanan eksternal berbayar.
- OS-4: Gambar dan audio — tanpa OCR/LLM gambar hanya menghasilkan metadata, dan audio butuh transkripsi eksternal; diputuskan di D-1.
- OS-5: Editor Markdown (mengedit hasil di browser) — hanya pratinjau read-only pada MVP.
- OS-6: Format legacy `.doc`, `.ppt`, dan `.rst` — tidak tercantum dalam daftar format resmi markitdown (D-2).
- OS-7: API key, kuota per pengguna, dan billing.
- OS-8: Internasionalisasi (UI hanya Bahasa Indonesia pada MVP).
- OS-9: CI/CD dan deployment otomatis — dikerjakan di spec terpisah setelah MVP lokal berjalan.
- OS-10: Pembatalan konversi di sisi server saat timeout — thread konversi tidak bisa dihentikan paksa; klien cukup menerima 504 (D-9).

---

## Decisions

Semua pertanyaan terbuka dari draf sebelumnya sudah diputuskan. Kolom Bukti menunjukkan apa yang sudah diverifikasi langsung (sandbox, markitdown 0.1.5, Python 3.12) dan apa yang belum.

| ID | Keputusan | Bukti / Catatan |
|----|-----------|-----------------|
| D-1 | Gambar dan audio **tidak** masuk MVP (OS-4). Dependensi yang dipasang: `markitdown[pdf,docx,pptx,xlsx,xls,youtube-transcription]>=0.1.5,<0.2`, bukan `[all]`. | Mengurangi dependensi dan permukaan serangan. Tidak butuh ffmpeg. |
| D-2 | Format yang didukung tepat 14 pada FR-5. `.doc`, `.ppt`, `.rst` dikeluarkan (OS-6). | Daftar resmi markitdown tidak memuat ketiganya. **Terverifikasi:** 14 format di FR-5 berhasil dikonversi lewat `convert_stream()` dengan fixture di `backend/tests/fixtures/`. **Temuan:** (a) `fake.pdf` berisi teks tetap "berhasil" jadi teks, sehingga FR-26 wajib; (b) ZIP dengan 101 entri dikonversi tanpa batas, sehingga NFR-S4 wajib; (c) `malware.exe` menghasilkan karakter sampah, sehingga allowlist FR-3 wajib; (d) `empty.pdf` melempar exception, tetapi EC-1 tetap dicek lebih dulu; (e) nama ZIP tampil `None` kecuali `StreamInfo(filename=...)` diberikan. README markitdown juga memperingatkan agar tidak meneruskan input tak tepercaya langsung. |
| D-3 | NFR-P2 (15 dtk) dan NFR-R2 (60 dtk) adalah target sementara. Pada Phase 2 diukur dengan benchmark; jika meleset, **spec yang direvisi**, bukan tes yang dilonggarkan diam-diam. Host backend belum dipilih; Dockerfile harus portabel. | Belum diukur (butuh host nyata). |
| D-4 | Rate limit in-memory per instance (mis. `slowapi`), satu instance di MVP. Jika nanti multi-instance, batas menjadi per instance dan perlu Redis. | NFR-SC1 mengacu pada data, bukan counter rate limit. |
| D-5 | Maksimum 20 file per batch dan total 100 MB per batch (FR-27). | 20 file x 50 MB tanpa batas total bisa mencapai 1 GB; ditambahkan agar memori terkendali. |
| D-6 | ZIP hasil batch dibuat di klien (`jszip`) agar backend tetap stateless. | |
| D-7 | Progres unggah nyata (axios `onUploadProgress`); konversi ditampilkan indeterminate karena backend tidak punya progres nyata. | AC-17 diuji dengan status, bukan persentase konversi. |
| D-8 | Pratinjau memakai `react-markdown` + `remark-gfm`, **tanpa** `rehype-raw`. `@uiw/react-md-editor` dihapus dari stack (editor di luar scope, OS-5). Split view memakai `react-resizable-panels`. | Alasan: NFR-S7. Konversi pptx menghasilkan komentar HTML (`<!-- Slide number: 1 -->`) sehingga HTML mentah memang muncul di output. |
| D-9 | markitdown bersifat sinkron: dijalankan lewat `asyncio.to_thread` dengan semaphore 3 (NFR-P3) dan `asyncio.wait_for` 60 detik (NFR-R2). Input dibaca dari `UploadFile.file` sebagai stream, tanpa menulis file permanen. Thread yang timeout tidak bisa dihentikan (OS-10). | Ukuran dicek saat membaca per chunk, bukan hanya dari header `Content-Length`. |
| D-10 | URL web biasa diambil oleh fetcher kita sendiri (`httpx`): validasi skema, resolve DNS dan tolak IP non-publik, redirect manual maksimum 5 dengan validasi ulang tiap hop, timeout 15 dtk, batas 20 MB, lalu hasilnya diteruskan ke `convert_stream()`. URL YouTube hanya untuk host `youtube.com`, `www.youtube.com`, `m.youtube.com`, `youtu.be` dan diteruskan ke markitdown. | **Belum terverifikasi:** konversi URL dan YouTube tidak bisa diuji di sandbox (tanpa akses jaringan). Transkrip YouTube dari IP datacenter sering diblokir; itu ditangani EC-12, bukan bug. |
| D-11 | Python 3.12. Versi Next.js dan Tailwind **dikunci saat instalasi** dengan memeriksa rilis stabil terbaru, lalu dicatat di `CHANGELOG.md`. | Plan menyebut Next 15 dan Tailwind 3, tetapi `create-next-app` bisa memasang versi lebih baru. |
| D-12 | Validasi file berlapis: allowlist ekstensi (case-insensitive) lalu magic bytes lalu batas ukuran saat streaming. | FR-3, FR-26, FR-4, EC-19. |
| D-13 | UI hanya Bahasa Indonesia (OS-8). Pesan error API juga Bahasa Indonesia; kode error tetap bahasa Inggris. | |

### Catatan konsistensi dengan project plan awal

1. `create-next-app ... --no-src-dir` bertentangan dengan struktur `src/` di plan; pakai `--src-dir`.
2. `NEXT_PUBLIC_API_URL=http://backend:8000` di docker-compose tidak bekerja dari browser; untuk lokal pakai `http://localhost:8000`.
3. Plan tidak menyebut perlindungan SSRF dan XSS pratinjau; ditambahkan sebagai FR-12, NFR-S6, NFR-S7.
4. `MAX_FILE_SIZE_MB` saja tidak cukup untuk batch; ditambahkan `MAX_BATCH_SIZE_MB`.
