"""Backend tests untuk SPEC-001 (markitdown-web).

Sumber: specs/SPEC-001-markitdown-web.md
RED phase: test stub — NotImplementedError. Implementasi per phase sesuai IMPLEMENTATION_PLAN.md.
Fixtures: jalankan `python scripts/make_fixtures.py` sekali. File ada di tests/fixtures/.

Perintah:
    python -m pytest -q                    # jalankan semua
    python -m pytest -q -k "ac11"          # jalankan satu test
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

FIXTURES = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_client():
    """Membuat TestClient setelah app tersedia (Phase 1+)."""
    from app.main import app
    return TestClient(app, raise_server_exceptions=False)


# ===========================================================================
# PHASE 1 — Skeleton backend (AC-11, AC-12, AC-23)
# ===========================================================================

class TestPhase1Skeleton:

    def test_ac11_health_check(self):
        """AC-11: Health check [FR-13, NFR-P1] — GET /api/health → 200, status=ok"""
        client = make_client()
        resp = client.get("/api/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert "version" in body

    def test_ac12_cors_membatasi_origin(self):
        """AC-12: CORS membatasi origin [FR-14]
        ALLOWED_ORIGINS=http://localhost:3000 → evil.example tidak dapat Access-Control-Allow-Origin
        """
        import os
        os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")
        client = make_client()
        resp = client.get(
            "/api/health",
            headers={"Origin": "https://evil.example"},
        )
        # Header tidak boleh ada untuk origin asing
        acao = resp.headers.get("access-control-allow-origin", "")
        assert acao != "https://evil.example", (
            "CORS harus menolak origin yang tidak terdaftar"
        )

    def test_ac23_error_tidak_membocorkan_detail_internal(self):
        """AC-23: Error tidak membocorkan detail internal [NFR-R1]
        Path tidak dikenal → 404; body harus JSON dengan error & message, tanpa traceback.
        """
        client = make_client()
        resp = client.post("/api/convert/file")  # belum ada di Phase 1 → 404 atau 422
        body = resp.json()
        body_str = str(body)
        # Harus ada field standar
        assert "error" in body or resp.status_code in (404, 405, 422)
        # TIDAK boleh ada stack trace
        assert "Traceback" not in body_str
        assert "File \"" not in body_str


# ===========================================================================
# PHASE 2 — Konversi satu file (AC-1..AC-3, AC-5, AC-6, AC-24, AC-29)
# ===========================================================================

class TestPhase2ConvertFile:

    def test_ac1_konversi_satu_file_berhasil(self):
        """AC-1: Konversi satu file berhasil [FR-1, FR-5]"""
        raise NotImplementedError("AC-1 — Phase 2")

    def test_ac2_ekstensi_tidak_didukung_ditolak(self):
        """AC-2: Ekstensi tidak didukung ditolak [FR-3]"""
        raise NotImplementedError("AC-2 — Phase 2")

    def test_ac3_file_terlalu_besar_ditolak(self):
        """AC-3: File terlalu besar ditolak [FR-4]"""
        raise NotImplementedError("AC-3 — Phase 2")

    def test_ac5_file_sementara_dibersihkan(self):
        """AC-5: File sementara dibersihkan [FR-7]"""
        raise NotImplementedError("AC-5 — Phase 2")

    def test_ac6_format_inti_terkonversi(self):
        """AC-6: Format inti terkonversi [FR-5] — 14 format"""
        raise NotImplementedError("AC-6 — Phase 2")

    def test_ac24_konversi_tidak_memakai_convert_dengan_input_pengguna(self):
        """AC-24: Konversi tidak memakai convert() dengan input pengguna [FR-8]
        Static check: tidak ada MarkItDown.convert( di converter.py
        """
        converter_path = Path(__file__).parent.parent / "app" / "services" / "converter.py"
        if not converter_path.exists():
            raise NotImplementedError("AC-24 — Phase 2: converter.py belum ada")
        source = converter_path.read_text(encoding="utf-8")
        # Tidak boleh ada .convert( diikuti variabel dari user
        assert "MarkItDown().convert(" not in source, (
            "Jangan pakai MarkItDown().convert() langsung (FR-8)"
        )

    def test_ac29_isi_file_tidak_cocok_dengan_ekstensi(self):
        """AC-29: Isi file tidak cocok dengan ekstensi [FR-26]"""
        raise NotImplementedError("AC-29 — Phase 2")

    def test_ec1_file_kosong_0_byte(self):
        """EC-1: File kosong (0 byte) → HTTP 422 EMPTY_FILE"""
        raise NotImplementedError("EC-1 — Phase 2")

    def test_ec2_ekstensi_benar_tetapi_isi_bukan_format_tersebut(self):
        """EC-2: fake.pdf berisi teks biasa → INVALID_FILE_CONTENT"""
        raise NotImplementedError("EC-2 — Phase 2")

    def test_ec3_pdf_terenkripsi_berpassword(self):
        """EC-3: PDF terenkripsi → CONVERSION_FAILED"""
        raise NotImplementedError("EC-3 — Phase 2")

    def test_ec4_pdf_hasil_scan_tanpa_lapisan_teks(self):
        """EC-4: PDF tanpa teks → 200 + warnings NO_TEXT_EXTRACTED"""
        raise NotImplementedError("EC-4 — Phase 2")

    def test_ec5_nama_file_mengandung_path_traversal(self):
        """EC-5: Path traversal di nama file → nama tersanitasi"""
        raise NotImplementedError("EC-5 — Phase 2")

    def test_ec19_file_berekstensi_huruf_besar_atau_campuran(self):
        """EC-19: REPORT.PDF → diperlakukan sama dengan .pdf"""
        raise NotImplementedError("EC-19 — Phase 2")


# ===========================================================================
# PHASE 3 — Hardening: ZIP, timeout, rate limit
# ===========================================================================

class TestPhase3Hardening:

    def test_ac13_rate_limit(self):
        """AC-13: Rate limit [NFR-S2] — request ke-31 → 429 RATE_LIMITED"""
        raise NotImplementedError("AC-13 — Phase 3")

    def test_ac14_zip_bomb_ditolak(self):
        """AC-14: Zip bomb ditolak [NFR-S4] — 101 entri → 422 ARCHIVE_LIMIT_EXCEEDED"""
        raise NotImplementedError("AC-14 — Phase 3")

    def test_ac15_timeout_konversi(self):
        """AC-15: Timeout konversi [NFR-R2] — > 60 dtk → 504 CONVERSION_TIMEOUT"""
        raise NotImplementedError("AC-15 — Phase 3")

    def test_ac32_zip_berisi_file_di_luar_allowlist_ditolak(self):
        """AC-32: ZIP berisi .exe atau nested ZIP → 422 ARCHIVE_CONTENT_NOT_ALLOWED"""
        raise NotImplementedError("AC-32 — Phase 3")

    def test_ec14_pengguna_menutup_tab_saat_konversi_berjalan(self):
        """EC-14: Client disconnect → server tetap hapus temp file"""
        raise NotImplementedError("EC-14 — Phase 3")

    def test_ec18_zip_berisi_entri_di_luar_allowlist(self):
        """EC-18: ZIP nested / exe → ARCHIVE_CONTENT_NOT_ALLOWED"""
        raise NotImplementedError("EC-18 — Phase 3")


# ===========================================================================
# PHASE 4 — Batch
# ===========================================================================

class TestPhase4Batch:

    def test_ac4_batch_dengan_campuran_sukses_dan_gagal(self):
        """AC-4: Batch campuran [FR-2, FR-6]"""
        raise NotImplementedError("AC-4 — Phase 4")

    def test_ac31_batch_melebihi_total_ukuran(self):
        """AC-31: Batch > MAX_BATCH_SIZE_MB → 413 BATCH_TOO_LARGE"""
        raise NotImplementedError("AC-31 — Phase 4")

    def test_ec6_dua_file_dengan_nama_sama_dalam_satu_batch(self):
        """EC-6: Dua file nama sama → keduanya diproses"""
        raise NotImplementedError("EC-6 — Phase 4")

    def test_ec7_request_batch_tanpa_file(self):
        """EC-7: Batch kosong → 422 NO_FILES"""
        raise NotImplementedError("EC-7 — Phase 4")

    def test_ec8_batch_melebihi_20_file(self):
        """EC-8: > 20 file → 422 TOO_MANY_FILES"""
        raise NotImplementedError("EC-8 — Phase 4")

    def test_ec17_total_ukuran_batch_max_batch_size_mb(self):
        """EC-17: Total > MAX_BATCH_SIZE_MB → 413 BATCH_TOO_LARGE"""
        raise NotImplementedError("EC-17 — Phase 4")


# ===========================================================================
# PHASE 5 — URL & YouTube
# ===========================================================================

class TestPhase5Url:

    def test_ac7_konversi_url_web_berhasil(self):
        """AC-7: Konversi URL web berhasil [FR-9, FR-11]"""
        raise NotImplementedError("AC-7 — Phase 5")

    def test_ac8_konversi_youtube_berhasil(self):
        """AC-8: Konversi YouTube berhasil [FR-10]"""
        raise NotImplementedError("AC-8 — Phase 5")

    def test_ac9_url_internal_ditolak(self):
        """AC-9: URL internal ditolak [FR-12]"""
        raise NotImplementedError("AC-9 — Phase 5")

    def test_ac10_skema_selain_http_https_ditolak(self):
        """AC-10: Skema selain http/https ditolak [FR-11]"""
        raise NotImplementedError("AC-10 — Phase 5")

    def test_ec9_url_tidak_bisa_dijangkau(self):
        """EC-9: URL unreachable → 502 URL_FETCH_FAILED"""
        raise NotImplementedError("EC-9 — Phase 5")

    def test_ec10_url_redirect_ke_alamat_privat(self):
        """EC-10: Redirect ke IP privat → URL_NOT_ALLOWED"""
        raise NotImplementedError("EC-10 — Phase 5")

    def test_ec11_video_youtube_tanpa_transkrip(self):
        """EC-11: YouTube tanpa transkrip → 422 TRANSCRIPT_UNAVAILABLE"""
        raise NotImplementedError("EC-11 — Phase 5")

    def test_ec12_youtube_membatasi_laju(self):
        """EC-12: YouTube throttle → 503 UPSTREAM_THROTTLED"""
        raise NotImplementedError("EC-12 — Phase 5")
