> **CATATAN:** Dokumen ini adalah rencana awal. Jika berbeda dengan `specs/SPEC-001-markitdown-web.md`, **spec yang berlaku** (lihat bagian Decisions di spec). Perbedaan utama: `@uiw/react-md-editor` diganti `react-markdown`, `aiofiles` tidak dipakai, `markitdown[all]` diganti extras terpilih, ditambah perlindungan SSRF/XSS.

# 📋 Project Preparation: markitdown-web

> Website converter all-format → Markdown menggunakan library [markitdown](https://github.com/microsoft/markitdown) (Microsoft)

---

## 🎯 Overview

| Item | Detail |
|------|--------|
| **Nama Project** | `markitdown-web` |
| **Tujuan** | Website untuk mengkonversi berbagai format file ke Markdown (`.md`) |
| **Backend** | FastAPI (Python) — memanfaatkan library `markitdown` langsung |
| **Frontend** | Next.js (React) |
| **Deployment** | Cloud (Vercel untuk frontend, Railway/Fly.io untuk backend) |
| **Repo** | Terpisah dari repo `markitdown` asli |

---

## 🛠 Tech Stack

### Backend
| Teknologi | Versi | Kegunaan |
|-----------|-------|----------|
| Python | ≥ 3.10 | Runtime |
| FastAPI | latest | REST API framework |
| Uvicorn | latest | ASGI server |
| markitdown | `[all]` | Core converter engine |
| python-multipart | latest | Handle file upload |
| aiofiles | latest | Async file I/O |

### Frontend
| Teknologi | Versi | Kegunaan |
|-----------|-------|----------|
| Next.js | 15.x | Full-stack React framework |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.x | Styling |
| @uiw/react-md-editor | latest | Markdown preview/editor |
| react-dropzone | latest | Drag & Drop upload |
| axios | latest | HTTP client |
| zustand | latest | State management |
| sonner | latest | Toast notifications |

---

## 📁 Struktur Folder

```
markitdown-web/              ← Root repository baru
├── README.md
├── .gitignore
├── docker-compose.yml       ← Untuk development lokal
│
├── backend/                 ← FastAPI Python Backend
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── app/
│       ├── __init__.py
│       ├── main.py          ← FastAPI entry point
│       ├── config.py        ← Environment config
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── convert.py   ← /api/convert endpoints
│       │   └── health.py    ← /api/health
│       ├── services/
│       │   ├── __init__.py
│       │   └── converter.py ← Wrapper untuk markitdown
│       ├── models/
│       │   ├── __init__.py
│       │   └── schemas.py   ← Pydantic schemas
│       └── utils/
│           ├── __init__.py
│           └── file_utils.py
│
└── frontend/                ← Next.js Frontend
    ├── package.json
    ├── tsconfig.json
    ├── next.config.ts
    ├── .env.local.example
    ├── Dockerfile
    ├── public/
    │   └── favicon.ico
    └── src/
        ├── app/
        │   ├── layout.tsx
        │   ├── page.tsx     ← Landing/Main page
        │   └── globals.css
        ├── components/
        │   ├── ui/          ← Reusable UI components
        │   ├── DropZone.tsx     ← Drag & Drop file uploader
        │   ├── UrlInput.tsx     ← YouTube / URL input
        │   ├── FileQueue.tsx    ← Batch upload queue
        │   ├── MarkdownPreview.tsx ← Split view preview
        │   ├── ProgressBar.tsx
        │   ├── ThemeToggle.tsx  ← Dark/Light mode
        │   └── DownloadButton.tsx
        ├── hooks/
        │   ├── useConvert.ts
        │   └── useTheme.ts
        ├── store/
        │   └── convertStore.ts  ← Zustand store
        ├── services/
        │   └── api.ts           ← API calls ke backend
        └── types/
            └── index.ts
```

---

## 🔌 API Design (Backend)

### Base URL: `/api`

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `GET` | `/health` | Health check |
| `POST` | `/convert/file` | Upload satu file, convert ke MD |
| `POST` | `/convert/files` | Upload banyak file (batch), convert ke MD |
| `POST` | `/convert/url` | Convert dari URL (YouTube, web, dll) |

### Request & Response

**`POST /api/convert/file`**
```
Content-Type: multipart/form-data
Body: file (binary)

Response 200:
{
  "filename": "document.pdf",
  "markdown": "# Document Title\n...",
  "size_bytes": 12345,
  "converted_at": "2026-10-24T09:00:00Z"
}
```

**`POST /api/convert/url`**
```json
{
  "url": "https://www.youtube.com/watch?v=..."
}

Response 200:
{
  "source_url": "https://...",
  "markdown": "# Video Title\n...",
  "converted_at": "2026-10-24T09:00:00Z"
}
```

**`POST /api/convert/files` (Batch)**
```
Content-Type: multipart/form-data
Body: files[] (multiple binaries)

Response 200:
{
  "results": [
    { "filename": "doc1.pdf", "markdown": "...", "status": "success" },
    { "filename": "doc2.pptx", "markdown": "...", "status": "success" },
    { "filename": "broken.xyz", "markdown": null, "status": "error", "error": "..." }
  ],
  "total": 3,
  "success": 2,
  "failed": 1
}
```

---

## 🎨 Fitur Website

### ✅ Fitur yang akan dibangun

1. **Drag & Drop File Upload**
   - Seret file langsung ke area upload
   - Visual feedback saat dragging
   - Validasi tipe file

2. **Batch Upload**
   - Upload beberapa file sekaligus
   - Queue list dengan status per file
   - Progress individual per file

3. **URL Input**
   - Support YouTube URL → transcript
   - Support web page URL → HTML to MD

4. **Split View Preview**
   - Sisi kiri: info file + raw markdown
   - Sisi kanan: rendered markdown preview
   - Resizable split pane

5. **Download `.md` File**
   - Download per file
   - Download semua hasil sebagai ZIP (batch)

6. **Dark Mode / Light Mode**
   - Toggle manual
   - Ikuti system preference secara default

7. **Real-time Progress Bar**
   - Indikasi proses upload & konversi
   - Per-file progress untuk batch

---

## 🚀 Format File yang Didukung

Diambil dari kemampuan `markitdown[all]`:

| Kategori | Format |
|----------|--------|
| Document | PDF, DOCX, DOC |
| Presentation | PPTX, PPT |
| Spreadsheet | XLSX, XLS, CSV |
| Web | HTML, HTM |
| Data | JSON, XML |
| Media | Images (JPEG, PNG, dll), Audio (WAV, MP3) |
| Archive | ZIP |
| eBook | EPUB |
| URL | YouTube, web pages |
| Text | TXT, MD, RST |

---

## 🏗 Setup Steps (Langkah Persiapan)

### Step 1: Buat Folder & Init Git

```bash
# Buat folder project baru (terpisah dari markitdown)
mkdir markitdown-web
cd markitdown-web
git init
```

### Step 2: Setup Backend (FastAPI)

```bash
cd backend

# Buat virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install fastapi uvicorn python-multipart aiofiles
pip install 'markitdown[all]'

# (Opsional) Jika pakai YouTube transcription
pip install 'markitdown[youtube-transcription]'
```

### Step 3: Setup Frontend (Next.js)

```bash
cd frontend

# Init Next.js dengan TypeScript
npx create-next-app@latest . --typescript --tailwind --eslint --app --no-src-dir

# Rename ke src structure jika perlu
# Install tambahan dependencies
npm install @uiw/react-md-editor react-dropzone axios zustand sonner
npm install -D @types/node
```

### Step 4: Environment Variables

**Backend `.env`:**
```env
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000
MAX_FILE_SIZE_MB=50
UPLOAD_DIR=./tmp/uploads
```

**Frontend `.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 5: Run Development

```bash
# Terminal 1 - Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

---

## ☁️ Deployment Strategy

### Frontend → Vercel

```bash
# Deploy otomatis dari GitHub ke Vercel
# Set environment variable di Vercel dashboard:
# NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

### Backend → Railway

```bash
# Railway auto-detect Python + Dockerfile
# Set environment variables:
# ALLOWED_ORIGINS=https://your-frontend.vercel.app
# ENVIRONMENT=production
```

> [!TIP]
> Railway menyediakan free tier yang cukup untuk demo project. Alternatif: **Fly.io** (lebih fleksibel untuk Docker), atau **Render.com** (ada free tier dengan cold start).

### Alternatif: Docker Compose (Self-hosted)

```yaml
# docker-compose.yml (sudah ada di root project)
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - ALLOWED_ORIGINS=http://localhost:3000
  
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on: [backend]
```

---

## 📦 File yang Akan Dibuat (Output)

Semua file persiapan project ditulis sebagai dokumen `.md`:

- [x] `PROJECT_PLAN.md` — dokumen ini
- [ ] `backend/README.md` — dokumentasi backend
- [ ] `frontend/README.md` — dokumentasi frontend
- [ ] `API_SPEC.md` — spesifikasi API lengkap
- [ ] `DEPLOYMENT.md` — panduan deploy
- [ ] `CONTRIBUTING.md` — panduan kontribusi
- [ ] `CHANGELOG.md` — log perubahan

---

## ⚠️ Hal Penting yang Perlu Diperhatikan

> [!WARNING]
> **Security**: markitdown mengakses file dengan privilege proses saat ini. Di production, **wajib**:
> - Validasi tipe file sebelum konversi
> - Batasi ukuran file (max 50MB recommended)
> - Simpan file upload di direktori terisolasi (tmp)
> - Hapus file setelah konversi selesai
> - Gunakan `convert_stream()` atau `convert_local()` bukan `convert()` langsung

> [!NOTE]
> **YouTube Transcription**: Memerlukan `markitdown[youtube-transcription]` dan koneksi internet. Di production perlu rate limiting karena bisa kena throttle dari YouTube.

> [!IMPORTANT]
> **CORS**: Backend FastAPI harus dikonfigurasi CORS dengan benar, hanya allow domain frontend yang sudah dideploy.

---

## 🗓 Estimasi Pengerjaan

| Phase | Task | Estimasi |
|-------|------|----------|
| 1 | Setup project structure + backend skeleton | 1-2 jam |
| 2 | Core converter API (single file + URL) | 2-3 jam |
| 3 | Batch upload API | 1-2 jam |
| 4 | Frontend foundation + design system | 2-3 jam |
| 5 | Drag & Drop + file queue | 1-2 jam |
| 6 | Split view markdown preview | 2-3 jam |
| 7 | Dark mode + progress bar + polish | 1-2 jam |
| 8 | Deployment + CI/CD | 1-2 jam |
| **Total** | | **~11-19 jam** |

---

*Dokumen ini dibuat sebagai persiapan project `markitdown-web` — 2026-10-24*
