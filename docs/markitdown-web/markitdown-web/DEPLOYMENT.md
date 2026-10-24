# Deployment — markitdown-web

Dikerjakan pada Phase 9. Deployment otomatis/CI-CD di luar scope MVP (OS-9). Host backend belum dipilih (D-3); panduan ini sengaja netral.

## Arsitektur

Frontend (Next.js) dan backend (FastAPI) dideploy terpisah. Browser memanggil backend langsung, jadi CORS dan HTTPS wajib benar.

## Environment variables

Backend: `ENVIRONMENT=production`, `ALLOWED_ORIGINS=https://<domain-frontend>` (jangan `*`), `MAX_FILE_SIZE_MB`, `MAX_BATCH_SIZE_MB`, `RATE_LIMIT_PER_MIN`.
Frontend: `NEXT_PUBLIC_API_URL=https://<domain-backend>`. Variabel ini dibaca di browser dan di-bake saat build; ubah berarti build ulang.

## Pilihan host

Frontend: Vercel atau platform Next.js lain. Backend: platform yang menjalankan Docker (Railway, Fly.io, Render, atau VPS). Syarat backend: memori cukup untuk beberapa konversi paralel (semaphore 3, file hingga 50 MB; ukur di Phase 2), timeout request ≥ 60 detik, HTTPS. Cek batas gratis/tier terbaru di situs masing-masing; angkanya tidak dicatat di sini karena sering berubah.

## Checklist sebelum go-live

- [ ] `ALLOWED_ORIGINS` berisi tepat domain frontend; uji AC-12 terhadap domain produksi.
- [ ] HTTPS aktif di kedua domain (NFR-S1).
- [ ] `GET /api/health` 200.
- [ ] Container berjalan sebagai user non-root, tanpa volume upload permanen.
- [ ] Satu instance saja, atau terima bahwa rate limit bersifat per instance (D-4).
- [ ] Smoke test: unggah satu PDF, satu batch 2 file, satu URL web, satu video YouTube.
- [ ] Catat hasil di `CHANGELOG.md`.

## Catatan

Transkrip YouTube dari IP datacenter sering diblokir; respons `UPSTREAM_THROTTLED` atau `TRANSCRIPT_UNAVAILABLE` di produksi belum tentu bug (EC-11, EC-12).

## Docker Compose lokal

Dibuat di Phase 9. Gunakan `NEXT_PUBLIC_API_URL=http://localhost:8000` (bukan `http://backend:8000`, karena dibaca browser).
