"use client";

import { useState, useCallback } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// NFR-S7: rehype-raw TIDAK digunakan — mencegah XSS dari Markdown hasil konversi
// D-8: react-markdown + remark-gfm tanpa rehype-raw

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

  return (
    <section className="split-view" aria-label={`Pratinjau: ${filename ?? "hasil konversi"}`}>
      <div className="split-view__toolbar">
        <span className="split-view__filename">{filename ?? "Pratinjau"}</span>
        <button className="btn btn--ghost btn--sm" onClick={copy}>
          {copied ? "✓ Disalin" : "Salin Markdown"}
        </button>
      </div>

      {/* FR-19, FR-20, AC-27 — resizable split via react-resizable-panels v2 */}
      <PanelGroup direction="horizontal" className="split-view__panels">
        <Panel defaultSize={50} minSize={20} className="split-view__panel">
          <div className="split-view__panel-header">Markdown mentah</div>
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
          <div className="split-view__panel-header">Pratinjau render</div>
          <article className="split-view__rendered markdown-body">
            {/* AC-30: react-markdown tanpa rehype-raw mencegah injeksi HTML */}
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
