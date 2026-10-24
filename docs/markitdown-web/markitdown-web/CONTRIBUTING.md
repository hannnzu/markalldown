# Contributing

1. Perubahan perilaku dimulai dari spec: ubah `specs/SPEC-001-markitdown-web.md` dulu (atau buat SPEC-002), jalankan validator, baru tulis tes dan kode.
2. Satu commit per acceptance criterion atau kelompok edge case kecil. Format pesan: `feat(AC-7): konversi URL web` / `fix(EC-3): petakan PDF berpassword`.
3. Tes harus hijau sebelum merge: `python -m pytest -q` (backend), `npx vitest run` dan `npm run lint` (frontend).
4. Jangan melonggarkan tes agar lulus; jika target di spec tidak realistis, ubah spec dengan data.
5. Jangan menambahkan fitur yang tidak ada di spec atau yang tercantum di Out of Scope.
6. Pembaruan dependensi dicatat di `CHANGELOG.md`.
