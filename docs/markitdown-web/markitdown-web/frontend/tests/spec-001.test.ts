// Frontend tests for SPEC-001 (markitdown-web). Vitest + @testing-library/react.
// Generated from specs/SPEC-001-markitdown-web.md. RED phase: every test throws.
// Implement one at a time. Mock axios/network; never call a real backend here.
import { describe, it } from "vitest";

describe("SPEC-001 frontend", () => {
  it("AC-16: Validasi klien sebelum upload [FR-16]", () => {
    // Given pengguna menjatuhkan `photo.exe` dan file 60 MB ke DropZone
    // When validasi klien berjalan
    // Then tidak ada request jaringan dikirim untuk kedua file
    // Then toast error ditampilkan untuk masing-masing file
    throw new Error("not implemented: AC-16");
  });

  it("AC-17: Antrean menampilkan status per file [FR-17, FR-24]", () => {
    // Given pengguna menambahkan tiga file valid ke antrean
    // When konversi berjalan
    // Then tiap item menampilkan status `pending`, lalu `converting`, lalu `success` atau `error`
    // Then tiap item memiliki progress bar sendiri
    throw new Error("not implemented: AC-17");
  });

  it("AC-18: Split view [FR-19]", () => {
    // Given sebuah hasil konversi sukses dipilih dari antrean
    // When pratinjau dibuka
    // Then panel kiri menampilkan Markdown mentah
    // Then panel kanan menampilkan HTML hasil render dari Markdown yang sama
    throw new Error("not implemented: AC-18");
  });

  it("AC-19: Unduh .md [FR-21]", () => {
    // Given hasil sukses untuk file `laporan.docx`
    // When pengguna menekan tombol unduh
    // Then browser mengunduh file bernama `laporan.md` berisi Markdown hasil konversi
    throw new Error("not implemented: AC-19");
  });

  it("AC-20: Unduh ZIP batch [FR-22]", () => {
    // Given batch dengan 2 hasil sukses dan 1 hasil error
    // When pengguna menekan "Unduh semua"
    // Then browser mengunduh satu ZIP berisi tepat 2 file `.md`
    throw new Error("not implemented: AC-20");
  });

  it("AC-21: Tema default mengikuti sistem [FR-23]", () => {
    // Given pengguna belum pernah memilih tema dan sistem operasi memakai mode gelap
    // When halaman dimuat pertama kali
    // Then halaman tampil di mode gelap
    // Then toggle tema mengubah ke mode terang saat ditekan
    throw new Error("not implemented: AC-21");
  });

  it("AC-22: Upload bisa dioperasikan keyboard [NFR-A1]", () => {
    // Given fokus berada di area DropZone
    // When pengguna menekan Enter
    // Then dialog pemilih file terbuka
    throw new Error("not implemented: AC-22");
  });

  it("AC-25: Visual drag & drop [FR-15]", () => {
    // Given halaman utama terbuka
    // When pengguna menyeret sebuah file di atas DropZone
    // Then DropZone mendapat state visual "aktif" (atribut `data-dragging="true"`)
    // Then state tersebut hilang saat file dijatuhkan atau meninggalkan area
    throw new Error("not implemented: AC-25");
  });

  it("AC-26: Input URL di frontend [FR-18]", () => {
    // Given pengguna memasukkan URL YouTube valid ke UrlInput
    // When pengguna menekan tombol konversi
    // Then frontend mengirim `POST /api/convert/url` dengan body `{ "url": <nilai input> }`
    // Then sebuah item bertipe `url` muncul di antrean
    throw new Error("not implemented: AC-26");
  });

  it("AC-27: Split view bisa diubah ukurannya [FR-20]", () => {
    // Given split view terbuka dengan lebar panel kiri 50%
    // When pengguna menyeret pembatas ke kanan
    // Then lebar panel kiri bertambah dan lebar panel kanan berkurang
    // Then lebar total kedua panel tetap 100%
    throw new Error("not implemented: AC-27");
  });

  it("AC-28: Pesan error spesifik per file [FR-25]", () => {
    // Given batch dengan satu file yang gagal dengan `error` = `CONVERSION_FAILED`
    // When respons diterima
    // Then sebuah toast ditampilkan yang memuat nama file yang gagal
    // Then pesan toast sama dengan `message` dari backend
    throw new Error("not implemented: AC-28");
  });

  it("AC-30: Pratinjau tidak merender HTML berbahaya [NFR-S7]", () => {
    // Given Markdown berisi `<script>alert(1)</script>` dan `<img src=x onerror=alert(1)>`
    // When Markdown tersebut dirender di panel pratinjau
    // Then DOM panel tidak memuat elemen `script` maupun atribut `onerror`
    // Then teks tag tersebut tidak dieksekusi sebagai HTML
    throw new Error("not implemented: AC-30");
  });

  it("EC-13: Backend tidak bisa dijangkau dari frontend", () => {
    // Backend tidak bisa dijangkau dari frontend -> toast "Server tidak dapat dihubungi" dan item antrean ditandai `error`, bisa dicoba ulang
    throw new Error("not implemented: EC-13");
  });

  it("EC-15: Markdown hasil sangat besar (> 5 MB)", () => {
    // Markdown hasil sangat besar (> 5 MB) -> pratinjau tetap responsif dengan memotong render dan menampilkan peringatan; unduhan tetap menyertakan isi penuh
    throw new Error("not implemented: EC-15");
  });

  it("EC-16: Unggah file yang sama dua kali", () => {
    // Unggah file yang sama dua kali -> dua item antrean terpisah, tidak ada deduplikasi
    throw new Error("not implemented: EC-16");
  });

});
