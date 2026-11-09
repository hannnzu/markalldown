"use client";

import { useEffect, useCallback, useState } from "react";
import axios from "axios";
import { Sparkles, ArrowRightLeft, FileText, Globe, Layers, CheckCircle2 } from "lucide-react";

import DropZone from "@/components/DropZone";
import UrlInput from "@/components/UrlInput";
import QueueList from "@/components/QueueList";
import SplitView from "@/components/SplitView";
import MarkdownToPdf from "@/components/MarkdownToPdf";
import ThemeToggle from "@/components/ThemeToggle";
import { ToastContainer, useToast } from "@/components/Toast";
import { useQueueStore } from "@/store/queue";
import { useTheme } from "@/hooks/useTheme";
import { api } from "@/services/api";
import type { ApiError } from "@/types/api";

const MAX_BATCH = 20;

function extractErrorMessage(err: unknown, fallback = "Terjadi kesalahan"): { code: string; msg: string } {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data as ApiError | undefined;
    if (data?.error && data?.message) return { code: data.error, msg: data.message };
    if (err.response?.status === 429) return { code: "RATE_LIMITED", msg: "Terlalu banyak permintaan, coba lagi nanti" };
    if (!err.response) return { code: "NETWORK_ERROR", msg: "Server tidak dapat dihubungi" };
  }
  return { code: "INTERNAL_ERROR", msg: fallback };
}

export default function HomePage() {
  const { theme, setTheme } = useTheme();
  const { toasts, addToast, removeToast } = useToast();
  const { items, addFile, addUrl, setStatus, setProgress, setSuccess, setError, remove, clear } =
    useQueueStore();

  const [activeTab, setActiveTab] = useState<"to-md" | "to-pdf">("to-md");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Dengarkan error dari DropZone (validasi client-side) — AC-16
  useEffect(() => {
    const handler = (e: Event) => {
      const errors = (e as CustomEvent<string[]>).detail;
      errors.forEach((msg) => addToast("error", msg));
    };
    window.addEventListener("dropzone-error", handler);
    return () => window.removeEventListener("dropzone-error", handler);
  }, [addToast]);

  const convertFiles = useCallback(
    async (files: File[]) => {
      if (files.length === 0) return;

      if (files.length > MAX_BATCH) {
        addToast("error", `Maksimum ${MAX_BATCH} file per batch`);
        files = files.slice(0, MAX_BATCH);
      }

      if (files.length === 1) {
        const [file] = files;
        const id = addFile(file);
        setSelectedId(id);
        setStatus(id, "converting");
        try {
          const res = await api.convertFile(file, (pct) => setProgress(id, pct));
          setSuccess(id, res.markdown, res.converted_at, res.warnings);
          addToast("success", `Berhasil mengonversi '${file.name}'`);
          if (res.warnings.length > 0) {
            addToast("warning", `${res.filename}: ${res.warnings.join(", ")}`);
          }
        } catch (err) {
          const { code, msg } = extractErrorMessage(err, "Konversi gagal");
          setError(id, code, msg);
          addToast("error", `${file.name}: ${msg}`);
        }
      } else {
        const ids = files.map((f) => addFile(f));
        setSelectedId(ids[0]);
        ids.forEach((id) => setStatus(id, "converting"));
        try {
          const res = await api.convertFiles(files, (pct) => {
            ids.forEach((id) => setProgress(id, pct));
          });
          res.results.forEach((item, i) => {
            if (item.status === "success" && item.markdown) {
              setSuccess(ids[i], item.markdown, new Date().toISOString());
            } else {
              const msg = item.message ?? "Konversi gagal";
              setError(ids[i], item.error ?? "CONVERSION_FAILED", msg);
              addToast("error", `${item.filename}: ${msg}`);
            }
          });
          addToast("success", `${files.length} file batch berhasil diproses`);
        } catch (err) {
          const { code, msg } = extractErrorMessage(err, "Batch konversi gagal");
          ids.forEach((id) => setError(id, code, msg));
          addToast("error", msg);
        }
      }
    },
    [addFile, setStatus, setProgress, setSuccess, setError, addToast]
  );

  const convertUrl = useCallback(
    async (url: string) => {
      const id = addUrl(url);
      setSelectedId(id);
      setStatus(id, "converting");
      try {
        const res = await api.convertUrl(url);
        setSuccess(id, res.markdown, res.converted_at);
        addToast("success", "URL web / video berhasil diekstrak");
      } catch (err) {
        const { code, msg } = extractErrorMessage(err, "Konversi URL gagal");
        setError(id, code, msg);
        addToast("error", `${url}: ${msg}`);
      }
    },
    [addUrl, setStatus, setSuccess, setError, addToast]
  );

  const selectedItem = items.find((i) => i.id === selectedId) ?? items[0] ?? null;
  const isConverting = items.some((i) => i.status === "converting");

  return (
    <div className="page">
      {/* Enhanced Modern Header */}
      <header className="header">
        <div className="header__brand">
          <div className="header__logo-badge">
            <Sparkles size={20} className="text-primary-600" />
          </div>
          <div>
            <h1 className="header__title">MarkAllDown</h1>
            <p className="header__tagline">Dokumen Universal &bull; Markdown &bull; PDF Studio</p>
          </div>
        </div>

        <div className="header__actions">
          {/* Main Feature Tabs */}
          <nav className="tab-nav" aria-label="Pilihan Fitur">
            <button
              type="button"
              className={`tab-btn ${activeTab === "to-md" ? "tab-btn--active" : ""}`}
              onClick={() => setActiveTab("to-md")}
            >
              <ArrowRightLeft size={16} />
              <span>File &rarr; Markdown</span>
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === "to-pdf" ? "tab-btn--active" : ""}`}
              onClick={() => setActiveTab("to-pdf")}
            >
              <FileText size={16} />
              <span>Markdown &rarr; PDF</span>
            </button>
          </nav>

          <ThemeToggle theme={theme} onChange={setTheme} />
        </div>
      </header>

      <main className="main">
        {activeTab === "to-md" ? (
          <>
            {/* Hero & Badges */}
            <section className="hero-banner">
              <div className="hero-banner__pills">
                <span className="pill pill--accent">
                  <CheckCircle2 size={13} />
                  Engine: Microsoft MarkItDown v0.1.5
                </span>
                <span className="pill">PDF &bull; DOCX &bull; XLSX &bull; PPTX &bull; CSV &bull; EPUB &bull; YouTube</span>
              </div>
            </section>

            {/* Upload Area */}
            <section className="upload-section" aria-label="Unggah file">
              <DropZone onFiles={convertFiles} disabled={isConverting} />
              <div className="upload-section__divider">
                <span>atau masukkan URL website / video</span>
              </div>
              <UrlInput onSubmit={convertUrl} disabled={isConverting} />
            </section>

            {/* Results Section */}
            {items.length > 0 && (
              <section className="results-section">
                <QueueList
                  items={items}
                  selectedId={selectedItem?.id ?? null}
                  onSelect={setSelectedId}
                  onRemove={(id) => {
                    remove(id);
                    if (selectedId === id) setSelectedId(null);
                  }}
                  onClear={() => {
                    clear();
                    setSelectedId(null);
                  }}
                />

                {selectedItem?.markdown && (
                  <SplitView
                    markdown={selectedItem.markdown}
                    filename={selectedItem.name}
                  />
                )}
              </section>
            )}
          </>
        ) : (
          /* Feature: Markdown to PDF */
          <section className="pdf-studio-section" aria-label="Markdown to PDF Studio">
            <MarkdownToPdf onToast={addToast} />
          </section>
        )}
      </main>

      {/* Toast notifications */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
}
