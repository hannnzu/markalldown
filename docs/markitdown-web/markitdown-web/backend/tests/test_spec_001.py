"""Backend tests for SPEC-001 (markitdown-web).

Generated from specs/SPEC-001-markitdown-web.md. RED phase: every test raises NotImplementedError.
Implement one test at a time (simplest AC first), make it pass, commit.
Fixtures: run `python scripts/make_fixtures.py` once. Files live in tests/fixtures/.
"""

from pathlib import Path
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


class TestBackendSpec001:

    def test_ac1_konversi_satu_file_berhasil(self):
        """AC-1: Konversi satu file berhasil [FR-1, FR-5]"""
        # Given sebuah file `document.pdf` valid berukuran 1 MB
        # When klien mengirim `POST /api/convert/file` dengan file tersebut
        # Then respons berstatus 200
        # Then body memuat `filename` = `document.pdf`, `markdown` tidak kosong, `size_bytes` = 1048576 (ukuran asli), dan `converted_at` format ISO 8601
        # Fixture: sample.pdf
        raise NotImplementedError("AC-1")

    def test_ac2_ekstensi_tidak_didukung_ditolak(self):
        """AC-2: Ekstensi tidak didukung ditolak [FR-3]"""
        # Given file `malware.exe`
        # When klien mengirim `POST /api/convert/file`
        # Then respons berstatus 415
        # Then body memuat `error` = `UNSUPPORTED_FILE_TYPE`
        # Fixture: malware.exe
        raise NotImplementedError("AC-2")

    def test_ac3_file_terlalu_besar_ditolak(self):
        """AC-3: File terlalu besar ditolak [FR-4]"""
        # Given `MAX_FILE_SIZE_MB` = 50 dan sebuah file 51 MB
        # When klien mengirim `POST /api/convert/file`
        # Then respons berstatus 413
        # Then body memuat `error` = `FILE_TOO_LARGE`
        raise NotImplementedError("AC-3")

    def test_ac4_batch_dengan_campuran_sukses_dan_gagal(self):
        """AC-4: Batch dengan campuran sukses dan gagal [FR-2, FR-6]"""
        # Given tiga file: `doc1.pdf` valid, `doc2.pptx` valid, dan `broken.pdf` korup
        # When klien mengirim `POST /api/convert/files`
        # Then respons berstatus 200
        # Then `total` = 3, `success` = 2, `failed` = 1
        # Then entri `broken.pdf` memiliki `status` = `error` dan `markdown` = null
        # Fixture: sample.pdf, sample.pptx, fake.pdf/empty.pdf (korup)
        raise NotImplementedError("AC-4")

    def test_ac5_file_sementara_dibersihkan(self):
        """AC-5: File sementara dibersihkan [FR-7]"""
        # Given sebuah file valid dan sebuah file korup dikirim bergantian
        # When kedua konversi selesai
        # Then direktori upload temp tidak berisi file milik kedua request tersebut
        raise NotImplementedError("AC-5")

    def test_ac6_format_inti_terkonversi(self):
        """AC-6: Format inti terkonversi [FR-5]"""
        # Given satu contoh file valid untuk masing-masing format di FR-5
        # When tiap file dikirim ke `POST /api/convert/file`
        # Then tiap respons berstatus 200 dan `markdown` tidak kosong
        # Fixture: sample.* (14 format)
        raise NotImplementedError("AC-6")

    def test_ac7_konversi_url_web_berhasil(self):
        """AC-7: Konversi URL web berhasil [FR-9, FR-11]"""
        # Given URL `https://example.com`
        # When klien mengirim `POST /api/convert/url` dengan URL tersebut
        # Then respons berstatus 200
        # Then `source_url` = URL yang dikirim dan `markdown` tidak kosong
        raise NotImplementedError("AC-7")

    def test_ac8_konversi_youtube_berhasil(self):
        """AC-8: Konversi YouTube berhasil [FR-10]"""
        # Given URL video YouTube publik yang memiliki transkrip
        # When klien mengirim `POST /api/convert/url`
        # Then respons berstatus 200
        # Then `markdown` memuat teks transkrip
        raise NotImplementedError("AC-8")

    def test_ac9_url_internal_ditolak(self):
        """AC-9: URL internal ditolak [FR-12]"""
        # Given URL `http://127.0.0.1:8000/api/health`, `http://169.254.169.254/`, dan `http://10.0.0.5/`
        # When masing-masing dikirim ke `POST /api/convert/url`
        # Then masing-masing respons berstatus 400
        # Then `error` = `URL_NOT_ALLOWED`
        raise NotImplementedError("AC-9")

    def test_ac10_skema_selain_http_https_ditolak(self):
        """AC-10: Skema selain http/https ditolak [FR-11]"""
        # Given URL `file:///etc/passwd` dan `ftp://example.com/a.txt`
        # When masing-masing dikirim ke `POST /api/convert/url`
        # Then masing-masing respons berstatus 400
        # Then `error` = `URL_NOT_ALLOWED`
        raise NotImplementedError("AC-10")

    def test_ac11_health_check(self):
        """AC-11: Health check [FR-13, NFR-P1]"""
        # Given backend berjalan
        # When klien memanggil `GET /api/health`
        # Then respons berstatus 200 dan `status` = `ok`
        raise NotImplementedError("AC-11")

    def test_ac12_cors_membatasi_origin(self):
        """AC-12: CORS membatasi origin [FR-14]"""
        # Given `ALLOWED_ORIGINS` = `http://localhost:3000`
        # When request datang dengan header `Origin: https://evil.example`
        # Then respons tidak memuat header `Access-Control-Allow-Origin` untuk origin tersebut
        raise NotImplementedError("AC-12")

    def test_ac13_rate_limit(self):
        """AC-13: Rate limit [NFR-S2]"""
        # Given satu IP telah mengirim 30 request ke `/api/convert/file` dalam 1 menit
        # When IP yang sama mengirim request ke-31 dalam menit yang sama
        # Then respons berstatus 429
        # Then `error` = `RATE_LIMITED`
        raise NotImplementedError("AC-13")

    def test_ac14_zip_bomb_ditolak(self):
        """AC-14: Zip bomb ditolak [NFR-S4]"""
        # Given sebuah ZIP dengan 101 entri
        # When dikirim ke `POST /api/convert/file`
        # Then respons berstatus 422
        # Then `error` = `ARCHIVE_LIMIT_EXCEEDED`
        # Fixture: too_many_entries.zip
        raise NotImplementedError("AC-14")

    def test_ac15_timeout_konversi(self):
        """AC-15: Timeout konversi [NFR-R2]"""
        # Given konversi yang berjalan lebih dari 60 detik
        # When batas waktu terlampaui
        # Then respons berstatus 504
        # Then `error` = `CONVERSION_TIMEOUT`
        # Then file sementara dihapus
        raise NotImplementedError("AC-15")

    def test_ac23_error_tidak_membocorkan_detail_internal(self):
        """AC-23: Error tidak membocorkan detail internal [NFR-R1]"""
        # Given konversi gagal karena exception internal
        # When respons dikembalikan
        # Then body berformat JSON dengan `error` dan `message`
        # Then body tidak memuat stack trace maupun path file server
        raise NotImplementedError("AC-23")

    def test_ac24_konversi_tidak_memakai_convert_dengan_input_pengguna(self):
        """AC-24: Konversi tidak memakai convert() dengan input pengguna [FR-8]"""
        # Given kode layanan konverter di backend
        # When pengujian statis (grep/AST) dijalankan terhadap `app/services/converter.py`
        # Then tidak ada pemanggilan `MarkItDown.convert(` dengan path atau URL yang berasal dari request
        # Then konversi file memakai `convert_stream(` atau `convert_local(`
        raise NotImplementedError("AC-24")

    def test_ac29_isi_file_tidak_cocok_dengan_ekstensi(self):
        """AC-29: Isi file tidak cocok dengan ekstensi [FR-26]"""
        # Given file `fake.pdf` yang berisi teks biasa (bukan PDF)
        # When klien mengirim `POST /api/convert/file`
        # Then respons berstatus 422
        # Then body memuat `error` = `INVALID_FILE_CONTENT`
        # Fixture: fake.pdf
        raise NotImplementedError("AC-29")

    def test_ac31_batch_melebihi_total_ukuran(self):
        """AC-31: Batch melebihi total ukuran [FR-27]"""
        # Given `MAX_BATCH_SIZE_MB` = 100 dan tiga file masing-masing 40 MB
        # When klien mengirim `POST /api/convert/files`
        # Then respons berstatus 413
        # Then body memuat `error` = `BATCH_TOO_LARGE`
        raise NotImplementedError("AC-31")

    def test_ac32_zip_berisi_file_di_luar_allowlist_ditolak(self):
        """AC-32: ZIP berisi file di luar allowlist ditolak [NFR-S4]"""
        # Given ZIP yang berisi `evil.exe` dan ZIP lain yang berisi ZIP bersarang
        # When masing-masing dikirim ke `POST /api/convert/file`
        # Then masing-masing respons berstatus 422
        # Then `error` = `ARCHIVE_CONTENT_NOT_ALLOWED`
        # Fixture: zip_with_exe.zip, nested.zip
        raise NotImplementedError("AC-32")

    def test_ec1_file_kosong_0_byte(self):
        """EC-1"""
        # File kosong (0 byte) -> HTTP 422 `EMPTY_FILE`
        # Fixture: empty.pdf
        raise NotImplementedError("EC-1")

    def test_ec2_ekstensi_benar_tetapi_isi_bukan_format_tersebut_mis_pdf_beri(self):
        """EC-2"""
        # Ekstensi benar tetapi isi bukan format tersebut (mis. `.pdf` berisi teks biasa) -> HTTP 422 `INVALID_FILE_CONTENT`. Pemeriksaan ini wajib ada di lapisan kita: markitdown diam-diam memperlakukan `fake.pdf` sebagai teks biasa dan mengembalikan hasil seolah sukses (terverifikasi, D-2)
        # Fixture: fake.pdf
        raise NotImplementedError("EC-2")

    def test_ec3_pdf_terenkripsi_berpassword(self):
        """EC-3"""
        # PDF terenkripsi/berpassword -> `CONVERSION_FAILED` dengan pesan yang menyebut file terproteksi
        # Fixture: encrypted.pdf (markitdown melempar PDFPasswordIncorrect -> petakan ke CONVERSION_FAILED)
        raise NotImplementedError("EC-3")

    def test_ec4_pdf_hasil_scan_tanpa_lapisan_teks(self):
        """EC-4"""
        # PDF hasil scan tanpa lapisan teks -> HTTP 200 dengan `markdown` kosong dan `warnings` berisi `NO_TEXT_EXTRACTED` (OCR di luar scope)
        # Fixture: no_text.pdf (markitdown mengembalikan string kosong -> 200 + warnings NO_TEXT_EXTRACTED)
        raise NotImplementedError("EC-4")

    def test_ec5_nama_file_mengandung_path_traversal_etc_passwd_pdf(self):
        """EC-5"""
        # Nama file mengandung path traversal (`../../etc/passwd.pdf`) -> nama diabaikan untuk penyimpanan, respons memakai nama yang sudah disanitasi
        raise NotImplementedError("EC-5")

    def test_ec6_dua_file_dengan_nama_sama_dalam_satu_batch(self):
        """EC-6"""
        # Dua file dengan nama sama dalam satu batch -> keduanya diproses; saat ZIP, nama kedua diberi akhiran `-1`
        raise NotImplementedError("EC-6")

    def test_ec7_request_batch_tanpa_file(self):
        """EC-7"""
        # Request batch tanpa file -> HTTP 422 `NO_FILES`
        raise NotImplementedError("EC-7")

    def test_ec8_batch_melebihi_20_file(self):
        """EC-8"""
        # Batch melebihi 20 file -> HTTP 422 `TOO_MANY_FILES` (batas 20, lihat D-5)
        raise NotImplementedError("EC-8")

    def test_ec9_url_tidak_bisa_dijangkau_dns_gagal_timeout_5xx(self):
        """EC-9"""
        # URL tidak bisa dijangkau (DNS gagal, timeout, 5xx) -> HTTP 502 `URL_FETCH_FAILED`
        raise NotImplementedError("EC-9")

    def test_ec10_url_redirect_ke_alamat_privat(self):
        """EC-10"""
        # URL redirect ke alamat privat -> ditolak `URL_NOT_ALLOWED` (validasi dilakukan pada setiap hop redirect)
        raise NotImplementedError("EC-10")

    def test_ec11_video_youtube_tanpa_transkrip_atau_privat(self):
        """EC-11"""
        # Video YouTube tanpa transkrip atau privat -> HTTP 422 `TRANSCRIPT_UNAVAILABLE`
        raise NotImplementedError("EC-11")

    def test_ec12_youtube_membatasi_laju_throttle(self):
        """EC-12"""
        # YouTube membatasi laju (throttle) -> HTTP 503 `UPSTREAM_THROTTLED`
        raise NotImplementedError("EC-12")

    def test_ec14_pengguna_menutup_tab_saat_konversi_berjalan(self):
        """EC-14"""
        # Pengguna menutup tab saat konversi berjalan -> server menyelesaikan atau membatalkan konversi dan tetap menghapus file temp
        raise NotImplementedError("EC-14")

    def test_ec17_total_ukuran_batch_max_batch_size_mb(self):
        """EC-17"""
        # Total ukuran batch > `MAX_BATCH_SIZE_MB` -> HTTP 413 `BATCH_TOO_LARGE` sebelum file apa pun diproses
        raise NotImplementedError("EC-17")

    def test_ec18_zip_berisi_entri_berekstensi_di_luar_allowlist_atau_zip_bers(self):
        """EC-18"""
        # ZIP berisi entri berekstensi di luar allowlist atau ZIP bersarang -> HTTP 422 `ARCHIVE_CONTENT_NOT_ALLOWED`
        # Fixture: zip_with_exe.zip, nested.zip
        raise NotImplementedError("EC-18")

    def test_ec19_file_berekstensi_huruf_besar_atau_campuran_report_pdf(self):
        """EC-19"""
        # File berekstensi huruf besar atau campuran (`REPORT.PDF`) -> diperlakukan sama dengan huruf kecil
        raise NotImplementedError("EC-19")
