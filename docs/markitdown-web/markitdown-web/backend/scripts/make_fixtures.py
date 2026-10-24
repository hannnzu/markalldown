"""Generate small, valid sample files for every format in SPEC-001 FR-5.

Usage (from backend/):  python scripts/make_fixtures.py
Requires dev deps: python-docx python-pptx openpyxl xlwt reportlab ebooklib
Output: tests/fixtures/sample.<ext> plus a few deliberately bad files.
"""
from pathlib import Path
import io, json, zipfile

OUT = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
OUT.mkdir(parents=True, exist_ok=True)
TEXT = "Halo markitdown-web"


def w(name, data):
    p = OUT / name
    p.write_bytes(data.encode() if isinstance(data, str) else data)


def main():
    # --- plain / structured text
    w("sample.txt", f"{TEXT}\nbaris kedua\n")
    w("sample.md", f"# {TEXT}\n\n- satu\n- dua\n")
    w("sample.csv", "nama,nilai\nalpha,1\nbeta,2\n")
    w("sample.json", json.dumps({"judul": TEXT, "items": [1, 2, 3]}))
    w("sample.xml", f"<root><judul>{TEXT}</judul><item>1</item></root>")
    html = f"<html><head><title>{TEXT}</title></head><body><h1>{TEXT}</h1><p>paragraf</p></body></html>"
    w("sample.html", html)
    w("sample.htm", html)

    # --- office
    import docx
    d = docx.Document(); d.add_heading(TEXT, 1); d.add_paragraph("isi dokumen")
    b = io.BytesIO(); d.save(b); w("sample.docx", b.getvalue())

    import pptx
    pr = pptx.Presentation(); s = pr.slides.add_slide(pr.slide_layouts[1])
    s.shapes.title.text = TEXT; s.placeholders[1].text = "isi slide"
    b = io.BytesIO(); pr.save(b); w("sample.pptx", b.getvalue())

    import openpyxl
    wb = openpyxl.Workbook(); ws = wb.active; ws.append(["nama", "nilai"]); ws.append([TEXT, 1])
    b = io.BytesIO(); wb.save(b); w("sample.xlsx", b.getvalue())

    import xlwt
    xb = xlwt.Workbook(); xs = xb.add_sheet("Sheet1"); xs.write(0, 0, "nama"); xs.write(1, 0, TEXT)
    b = io.BytesIO(); xb.save(b); w("sample.xls", b.getvalue())

    # --- pdf
    from reportlab.pdfgen import canvas
    b = io.BytesIO(); c = canvas.Canvas(b); c.drawString(72, 750, TEXT); c.save(); w("sample.pdf", b.getvalue())

    # EC-3: PDF terenkripsi (password: "rahasia"), EC-4: PDF tanpa lapisan teks
    b = io.BytesIO(); c = canvas.Canvas(b, encrypt="rahasia"); c.drawString(72, 750, TEXT); c.save()
    w("encrypted.pdf", b.getvalue())
    b = io.BytesIO(); c = canvas.Canvas(b); c.rect(100, 100, 200, 200, fill=1); c.save()
    w("no_text.pdf", b.getvalue())

    # --- epub
    from ebooklib import epub
    book = epub.EpubBook(); book.set_identifier("id1"); book.set_title(TEXT); book.set_language("id")
    ch = epub.EpubHtml(title="Bab 1", file_name="c1.xhtml", lang="id"); ch.content = f"<h1>{TEXT}</h1><p>isi</p>"
    book.add_item(ch); book.toc = (ch,); book.add_item(epub.EpubNcx()); book.add_item(epub.EpubNav()); book.spine = ["nav", ch]
    epub.write_epub(str(OUT / "sample.epub"), book)

    # --- zip (2 entries)
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("a.txt", "isi a"); z.writestr("b.csv", "x,y\n1,2\n")
    w("sample.zip", b.getvalue())

    # --- negative fixtures
    w("empty.pdf", b"")                                   # EC-1
    w("fake.pdf", "ini bukan pdf, cuma teks")             # EC-2
    w("malware.exe", b"MZ\x00\x00")                       # AC-2
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:                    # AC-14 (101 entries)
        for i in range(101):
            z.writestr(f"f{i}.txt", "x")
    w("too_many_entries.zip", b.getvalue())
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:                    # AC-32 (entry di luar allowlist)
        z.writestr("evil.exe", b"MZ\x00\x00")
    w("zip_with_exe.zip", b.getvalue())
    inner = io.BytesIO()
    with zipfile.ZipFile(inner, "w") as z:
        z.writestr("a.txt", "x")
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:                    # AC-32 (ZIP bersarang)
        z.writestr("inner.zip", inner.getvalue())
    w("nested.zip", b.getvalue())
    print("fixtures ->", OUT)


if __name__ == "__main__":
    main()
