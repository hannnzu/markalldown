"use client";

import { useState, useCallback, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { FileText, Download, Printer, Copy, Check, Upload, Trash2, Eye } from "lucide-react";

interface MarkdownToPdfProps {
  onToast: (type: "info" | "success" | "warning" | "error", message: string) => void;
}

const DEFAULT_MARKDOWN = `# Laporan Dokumen Profesional

Dokumen ini disusun dan dikonversi menggunakan fitur **Markdown to PDF** di **MarkAllDown**.

## 1. Pendahuluan
Markdown adalah format penulisan teks terstruktur yang ringan dan mudah dibaca. Fitur ini memungkinkan Anda mengekspor dokumen Markdown langsung menjadi **PDF berkualitas tinggi**.

### Fitur Utama:
- Dukungan tabel GitHub Flavored Markdown (GFM)
- Blok kode (Syntax formatting)
- Penomoran dan daftar terstruktur
- Tampilan dokumen siap cetak atau simpan sebagai PDF

---

## 2. Tabel Ringkasan

| Modul | Fungsi | Status |
| :--- | :--- | :--- |
| **Parser** | Parsing Markdown ke HTML | Aktif |
| **Style Engine** | Standard Print Layout (A4) | Siap Cetak |
| **Exporter** | Native Browser PDF Engine | 100% Client-Side |

---

## 3. Contoh Kode
\`\`\`javascript
function exportToPdf() {
  console.log("Mengekspor dokumen ke format PDF...");
  window.print();
}
\`\`\`

> *"Dokumen yang rapi meningkatkan efisiensi dan profesionalitas kerja."*
`;

export default function MarkdownToPdf({ onToast }: MarkdownToPdfProps) {
  const [markdown, setMarkdown] = useState<string>(DEFAULT_MARKDOWN);
  const [docTitle, setDocTitle] = useState<string>("Dokumen-Markdown");
  const [copied, setCopied] = useState<boolean>(false);
  const printRef = useRef<HTMLDivElement>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith(".md") && !file.name.endsWith(".markdown") && !file.name.endsWith(".txt")) {
      onToast("error", "Harap pilih file berformat .md atau .txt");
      return;
    }

    const titleWithoutExt = file.name.replace(/\.[^/.]+$/, "");
    setDocTitle(titleWithoutExt);

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setMarkdown(content);
      onToast("success", `File '${file.name}' berhasil dimuat!`);
    };
    reader.readAsText(file);
  };

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(markdown).then(() => {
      setCopied(true);
      onToast("info", "Teks Markdown disalin ke clipboard!");
      setTimeout(() => setCopied(false), 2000);
    });
  }, [markdown, onToast]);

  const handlePrintPdf = useCallback(() => {
    const originalTitle = document.title;
    document.title = `${docTitle || "Dokumen"}`;
    window.print();
    document.title = originalTitle;
  }, [docTitle]);

  return (
    <div className="md2pdf-container">
      {/* Action Header */}
      <div className="md2pdf-toolbar">
        <div className="md2pdf-toolbar__left">
          <div className="md2pdf-title-input">
            <FileText size={18} className="text-primary" />
            <input
              type="text"
              value={docTitle}
              onChange={(e) => setDocTitle(e.target.value)}
              placeholder="Nama file dokumen..."
              className="md2pdf-title-input__field"
              title="Nama file PDF saat dicetak/disimpan"
            />
          </div>
          <label className="btn btn--secondary btn--sm md2pdf-upload-btn">
            <Upload size={15} />
            <span>Muat .md</span>
            <input
              type="file"
              accept=".md,.markdown,.txt"
              onChange={handleFileUpload}
              className="sr-only"
            />
          </label>
        </div>

        <div className="md2pdf-toolbar__right">
          <button
            type="button"
            className="btn btn--ghost btn--sm"
            onClick={() => setMarkdown("")}
            title="Bersihkan editor"
          >
            <Trash2 size={15} />
            <span>Kosongkan</span>
          </button>

          <button
            type="button"
            className="btn btn--ghost btn--sm"
            onClick={handleCopy}
            title="Salin Markdown"
          >
            {copied ? <Check size={15} /> : <Copy size={15} />}
            <span>{copied ? "Disalin" : "Salin"}</span>
          </button>

          <button
            type="button"
            className="btn btn--primary btn--sm md2pdf-print-btn"
            onClick={handlePrintPdf}
            title="Cetak atau Simpan sebagai PDF (Ctrl + P)"
          >
            <Printer size={16} />
            <span>Ekspor / Cetak PDF</span>
          </button>
        </div>
      </div>

      {/* Editor & Preview Panels */}
      <div className="md2pdf-workspace">
        {/* Editor Input */}
        <div className="md2pdf-editor-panel">
          <div className="md2pdf-panel-header">
            <span>Editor Markdown</span>
            <span className="md2pdf-stats">
              {markdown.length} karakter &bull; {markdown.trim() ? markdown.trim().split(/\s+/).length : 0} kata
            </span>
          </div>
          <textarea
            value={markdown}
            onChange={(e) => setMarkdown(e.target.value)}
            placeholder="Ketik atau tempel (paste) Markdown di sini..."
            className="md2pdf-textarea"
            spellCheck={false}
          />
        </div>

        {/* Live A4 Print Preview */}
        <div className="md2pdf-preview-panel">
          <div className="md2pdf-panel-header">
            <span>
              <Eye size={14} style={{ display: "inline", marginRight: "4px" }} />
              Pratinjau PDF (Format Cetak A4)
            </span>
            <span className="md2pdf-hint">Gunakan 'Save as PDF' di dialog cetak</span>
          </div>

          <div className="md2pdf-sheet-wrapper">
            <div ref={printRef} id="printable-pdf-document" className="md2pdf-sheet markdown-body">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {markdown || "*Tidak ada konten untuk ditampilkan. Silakan ketik Markdown di panel kiri.*"}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

