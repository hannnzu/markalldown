"use client";

import { useCallback, useRef, useState } from "react";

// Allowlist ekstensi — FR-3, FR-5, AC-16
const ALLOWED_EXTS = new Set([
  "pdf", "docx", "pptx", "xlsx", "xls", "csv",
  "html", "htm", "json", "xml", "txt", "md", "epub", "zip",
]);

const MAX_FILE_SIZE_MB = 50; // default, FR-4

interface DropZoneProps {
  onFiles: (files: File[]) => void;
  disabled?: boolean;
}

export default function DropZone({ onFiles, disabled }: DropZoneProps) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const validate = useCallback((files: File[]): { valid: File[]; errors: string[] } => {
    const valid: File[] = [];
    const errors: string[] = [];
    for (const f of files) {
      const ext = f.name.split(".").pop()?.toLowerCase() ?? "";
      if (!ALLOWED_EXTS.has(ext)) {
        errors.push(`"${f.name}" — format tidak didukung (.${ext})`);
        continue;
      }
      if (f.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        errors.push(`"${f.name}" — melebihi batas ${MAX_FILE_SIZE_MB} MB`);
        continue;
      }
      valid.push(f);
    }
    return { valid, errors };
  }, []);

  const handle = useCallback(
    (files: FileList | null) => {
      if (!files || files.length === 0) return;
      const { valid, errors } = validate(Array.from(files));
      if (errors.length > 0) {
        // Dispatch custom event agar Toast dapat menampilkan error — AC-16
        window.dispatchEvent(new CustomEvent("dropzone-error", { detail: errors }));
      }
      if (valid.length > 0) onFiles(valid);
    },
    [onFiles, validate]
  );

  return (
    <div
      className={`dropzone ${dragging ? "dropzone--dragging" : ""} ${disabled ? "dropzone--disabled" : ""}`}
      data-dragging={dragging ? "true" : "false"}
      role="button"
      tabIndex={0}
      aria-label="Area unggah file — tekan Enter atau Space untuk memilih file"
      onKeyDown={(e) => {
        // AC-22 — keyboard accessible
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          inputRef.current?.click();
        }
      }}
      onClick={() => !disabled && inputRef.current?.click()}
      onDragEnter={(e) => { e.preventDefault(); if (!disabled) setDragging(true); }}
      onDragOver={(e) => { e.preventDefault(); }}
      onDragLeave={(e) => {
        // hanya reset jika benar-benar meninggalkan elemen (bukan child)
        if (!e.currentTarget.contains(e.relatedTarget as Node)) setDragging(false);
      }}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        if (!disabled) handle(e.dataTransfer.files);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        multiple
        className="dropzone__input"
        accept={Array.from(ALLOWED_EXTS).map((e) => `.${e}`).join(",")}
        onChange={(e) => handle(e.target.files)}
        tabIndex={-1}
        aria-hidden="true"
      />

      <div className="dropzone__content">
        <span className="dropzone__icon" aria-hidden="true">
          {dragging ? "📂" : "📁"}
        </span>
        <p className="dropzone__title">
          {dragging ? "Lepaskan file di sini" : "Seret & jatuhkan file, atau klik untuk memilih"}
        </p>
        <p className="dropzone__hint">
          PDF, DOCX, PPTX, XLSX, XLS, CSV, HTML, JSON, XML, TXT, MD, EPUB, ZIP — maks. {MAX_FILE_SIZE_MB} MB per file
        </p>
      </div>
    </div>
  );
}
