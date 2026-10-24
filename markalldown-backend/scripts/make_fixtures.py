"""Script pembuatan fixture deterministik untuk tests/fixtures/.

Jalankan sekali: python scripts/make_fixtures.py
Output harus stabil (git status bersih setelah dijalankan ulang).

Fixtures yang dibuat:
  sample.pdf, sample.docx, sample.pptx, sample.xlsx, sample.xls,
  sample.csv, sample.html, sample.htm, sample.json, sample.xml,
  sample.txt, sample.md, sample.epub, sample.zip
  fake.pdf (teks biasa, bukan PDF)
  empty.pdf (0 byte)
  malware.exe (bukan executable asli, hanya untuk test allowlist)
  encrypted.pdf (simulasi — markitdown akan gagal)
  no_text.pdf (PDF tanpa teks — markitdown kembalikan kosong)
  too_many_entries.zip (101 entri)
  zip_with_exe.zip (berisi evil.exe)
  nested.zip (ZIP berisi ZIP)
"""
from __future__ import annotations

import csv
import io
import json
import os
import struct
import zipfile
from pathlib import Path

FIXTURES = Path(__file__).parent.parent / "tests" / "fixtures"
FIXTURES.mkdir(parents=True, exist_ok=True)


def _write(name: str, content: bytes) -> None:
    path = FIXTURES / name
    path.write_bytes(content)
    print(f"  created: {path.name} ({len(content)} bytes)")


def make_txt():
    _write("sample.txt", b"Hello, markitdown!\nThis is a plain text fixture.\n")


def make_md():
    _write("sample.md", b"# Sample Markdown\n\nThis is **bold** and _italic_.\n")


def make_csv():
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["name", "value"])
    w.writerow(["foo", "1"])
    w.writerow(["bar", "2"])
    _write("sample.csv", buf.getvalue().encode())


def make_json():
    _write("sample.json", json.dumps({"key": "value", "list": [1, 2, 3]}, indent=2).encode())


def make_xml():
    _write(
        "sample.xml",
        b'<?xml version="1.0"?><root><item id="1">Hello</item></root>',
    )


def make_html():
    html = b"<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Hello</h1></body></html>"
    _write("sample.html", html)
    _write("sample.htm", html)


def make_pdf():
    # Minimal valid PDF (readable by pypdf)
    pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R"
        b"/Contents 4 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>>"
        b">>endobj\n"
        b"4 0 obj<</Length 44>>\nstream\nBT /F1 12 Tf 100 700 Td (Hello PDF) Tj ET\nendstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f \n"
        b"trailer<</Size 5/Root 1 0 R>>\nstartxref\n9\n%%EOF"
    )
    _write("sample.pdf", pdf)


def make_fake_pdf():
    """fake.pdf berisi teks biasa — untuk EC-2 / FR-26."""
    _write("fake.pdf", b"This is NOT a PDF file, just plain text.\n")


def make_empty():
    """empty.pdf 0 byte — EC-1."""
    _write("empty.pdf", b"")


def make_malware():
    """malware.exe bukan executable asli — hanya untuk test allowlist (AC-2)."""
    _write("malware.exe", b"MZ\x90\x00This is a fake PE header for testing only.\n")


def make_encrypted_pdf():
    """encrypted.pdf simulasi — bukan PDF yang benar-benar terenkripsi.
    Cukup membuat file ber-magic PDF tetapi kontennya rusak agar markitdown gagal.
    Untuk test EC-3 — bisa diganti dengan PDF terenkripsi nyata jika tersedia.
    """
    _write(
        "encrypted.pdf",
        b"%PDF-1.4\n%%EOF\n",  # PDF minimal tapi tanpa struktur → markitdown error
    )


def make_no_text_pdf():
    """no_text.pdf — PDF valid tanpa teks (hanya page kosong).
    markitdown mengembalikan string kosong → EC-4.
    """
    pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f \n"
        b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n9\n%%EOF"
    )
    _write("no_text.pdf", pdf)


def make_zip_fixtures():
    """ZIP fixtures untuk Phase 3."""
    # ZIP normal berisi sample.txt
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("sample.txt", "Hello from zip\n")
    _write("sample.zip", buf.getvalue())

    # too_many_entries.zip — 101 entri (AC-14)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for i in range(101):
            zf.writestr(f"file{i:03d}.txt", f"content {i}\n")
    _write("too_many_entries.zip", buf.getvalue())

    # zip_with_exe.zip — berisi evil.exe (AC-32, EC-18)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("evil.exe", b"MZ fake exe")
    _write("zip_with_exe.zip", buf.getvalue())

    # nested.zip — ZIP berisi ZIP (AC-32, EC-18)
    inner_buf = io.BytesIO()
    with zipfile.ZipFile(inner_buf, "w") as zf:
        zf.writestr("inner.txt", "inner content")
    inner_zip = inner_buf.getvalue()

    outer_buf = io.BytesIO()
    with zipfile.ZipFile(outer_buf, "w") as zf:
        zf.writestr("inner.zip", inner_zip)
    _write("nested.zip", outer_buf.getvalue())


def make_docx():
    try:
        from docx import Document
        doc = Document()
        doc.add_heading("Sample Document", 0)
        doc.add_paragraph("This is a sample DOCX fixture for markitdown testing.")
        buf = io.BytesIO()
        doc.save(buf)
        _write("sample.docx", buf.getvalue())
    except ImportError:
        print("  SKIP sample.docx — install python-docx to generate")


def make_pptx():
    try:
        from pptx import Presentation
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = "Sample Presentation"
        slide.placeholders[1].text = "Fixture for markitdown testing."
        buf = io.BytesIO()
        prs.save(buf)
        _write("sample.pptx", buf.getvalue())
    except ImportError:
        print("  SKIP sample.pptx — install python-pptx to generate")


def make_xlsx():
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        ws.append(["Name", "Value"])
        ws.append(["foo", 1])
        ws.append(["bar", 2])
        buf = io.BytesIO()
        wb.save(buf)
        _write("sample.xlsx", buf.getvalue())
    except ImportError:
        print("  SKIP sample.xlsx — install openpyxl to generate")


def make_xls():
    try:
        import xlwt
        wb = xlwt.Workbook()
        ws = wb.add_sheet("Sheet1")
        ws.write(0, 0, "Name")
        ws.write(0, 1, "Value")
        ws.write(1, 0, "foo")
        ws.write(1, 1, 1)
        buf = io.BytesIO()
        wb.save(buf)
        _write("sample.xls", buf.getvalue())
    except ImportError:
        print("  SKIP sample.xls — install xlwt to generate")


def make_epub():
    try:
        import ebooklib
        from ebooklib import epub
        book = epub.EpubBook()
        book.set_identifier("markalldown-fixture")
        book.set_title("Sample EPUB")
        book.set_language("en")
        c1 = epub.EpubHtml(title="Intro", file_name="intro.xhtml", lang="en")
        c1.content = b"<html><body><h1>Sample EPUB</h1><p>Fixture.</p></body></html>"
        book.add_item(c1)
        book.toc = (epub.Link("intro.xhtml", "Intro", "intro"),)
        book.spine = ["nav", c1]
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        buf = io.BytesIO()
        epub.write_epub(buf, book)
        _write("sample.epub", buf.getvalue())
    except ImportError:
        print("  SKIP sample.epub — install ebooklib to generate")


if __name__ == "__main__":
    print("Generating fixtures...")
    make_txt()
    make_md()
    make_csv()
    make_json()
    make_xml()
    make_html()
    make_pdf()
    make_fake_pdf()
    make_empty()
    make_malware()
    make_encrypted_pdf()
    make_no_text_pdf()
    make_zip_fixtures()
    make_docx()
    make_pptx()
    make_xlsx()
    make_xls()
    make_epub()
    print("Done! Run `git status` — should be clean if fixtures are deterministic.")
