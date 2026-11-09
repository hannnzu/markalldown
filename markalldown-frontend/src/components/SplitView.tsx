"use client";

import { useState, useCallback } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, Check, Download, FileText } from "lucide-react";

const PREVIEW_TRUNCATE = 5 * 1024 * 1024; // 5 MB — EC-15

interface SplitViewProps {
  markdown: string;
  filename?: string;
}

export default function SplitView({ markdown, filename }: SplitViewProps) {
  const [copied, setCopied] = useState(false);
  const isTruncated = markdown.length > PREVIEW_TRUNCATE;
  const previewText = isTruncated ? markdown.slice(0, PREVIEW_TRUNCATE) : markdown;

  const copy = useCallback(() => {
    navigator.clipboard.writeText(markdown).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [markdown]);

  const downloadMd = useCallback(() => {
    const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const name = filename ? filename.replace(/\.[^/.]+$/, "") + ".md" : "converted.md";
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [markdown, filename]);

  return (
    <section className="split-view" aria-label={`Pratinjau: ${filename ?? "hasil konversi"}`}>
      <div className="split-view__toolbar">
        <div className="split-view__toolbar-left">
          <FileText size={16} className="text-primary" />
          <span className="split-view__filename">{filename ?? "Pratinjau Hasil"}</span>
        </div>
        <div className="split-view__toolbar-right">
          <button className="btn btn--ghost btn--sm" onClick={downloadMd} title="Download file .md">
            <Download size={14} />
            <span>Unduh .md</span>
          </button>
          <button className="btn btn--secondary btn--sm" onClick={copy}>
            {copied ? <Check size={14} /> : <Copy size={14} />}
            <span>{copied ? "Disalin" : "Salin Markdown"}</span>
          </button>
        </div>
      </div>

      <PanelGroup direction="horizontal" className="split-view__panels">
        <Panel defaultSize={50} minSize={20} className="split-view__panel">
          <div className="split-view__panel-header">
            <span>Markdown mentah</span>
            <span className="text-xs text-muted">{markdown.length} karakter</span>
          </div>
          <pre className="split-view__raw">
            {previewText}
            {isTruncated && (
              <span className="split-view__truncate-notice">
                {"\n\n"}⚠️ Teks dipotong untuk performa. Unduh file untuk konten lengkap.
              </span>
            )}
          </pre>
        </Panel>

        <PanelResizeHandle className="split-view__handle" aria-label="Ubah ukuran panel" />

        <Panel defaultSize={50} minSize={20} className="split-view__panel">
          <div className="split-view__panel-header">
            <span>Pratinjau render</span>
            <span className="text-xs text-muted">HTML formatted</span>
          </div>
          <article className="split-view__rendered markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {previewText}
            </ReactMarkdown>
            {isTruncated && (
              <p className="split-view__truncate-notice">
                ⚠️ Pratinjau dipotong di {(PREVIEW_TRUNCATE / 1024 / 1024).toFixed(0)} MB. Unduh file untuk konten lengkap.
              </p>
            )}
          </article>
        </Panel>
      </PanelGroup>
    </section>
  );
}
