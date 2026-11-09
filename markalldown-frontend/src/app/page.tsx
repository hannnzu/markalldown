"use client";

import { useEffect, useCallback, useState } from "react";
import axios from "axios";

import DropZone from "@/components/DropZone";
import UrlInput from "@/components/UrlInput";
import QueueList from "@/components/QueueList";
import SplitView from "@/components/SplitView";
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

      // Batas 20 file — EC-8
      if (files.length > MAX_BATCH) {
        addToast("error", `Maksimum ${MAX_BATCH} file per batch`);
        files = files.slice(0, MAX_BATCH);
      }

      if (files.length === 1) {
        // Mode single file — FR-1
        const [file] = files;
        const id = addFile(file);
        setStatus(id, "converting");
        try {
          const res = await api.convertFile(file, (pct) => setProgress(id, pct));
          setSuccess(id, res.markdown, res.converted_at, res.warnings);
          if (res.warnings.length > 0) {
            addToast("warning", `${res.filename}: ${res.warnings.join(", ")}`);
          }
        } catch (err) {
          const { code, msg } = extractErrorMessage(err, "Konversi gagal");
          setError(id, code, msg);
          addToast("error", `${file.name}: ${msg}`);
        }
      } else {
        // Mode batch — FR-2
        const ids = files.map((f) => addFile(f));
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
      setStatus(id, "converting");
      try {
        const res = await api.convertUrl(url);
        setSuccess(id, res.markdown, res.converted_at);
      } catch (err) {
        const { code, msg } = extractErrorMessage(err, "Konversi URL gagal");
        setError(id, code, msg);
        addToast("error", `${url}: ${msg}`);
      }
    },
    [addUrl, setStatus, setSuccess, setError, addToast]
  );

  const selectedItem = items.find((i) => i.id === selectedId) ?? null;
  const isConverting = items.some((i) => i.status === "converting");

  return (
    <div className="page">
      {/* Header */}
      <header className="header">
        <div className="header__brand">
          <span className="header__logo" aria-hidden="true">📝</span>
          <h1 className="header__title">MarkAllDown</h1>
          <span className="header__tagline">Konversi apa pun ke Markdown</span>
        </div>
        <ThemeToggle theme={theme} onChange={setTheme} />
      </header>

      <main className="main">
        {/* Upload area */}
        <section className="upload-section" aria-label="Unggah file">
          <DropZone onFiles={convertFiles} disabled={isConverting} />
          <div className="upload-section__divider">
            <span>atau</span>
          </div>
          <UrlInput onSubmit={convertUrl} disabled={isConverting} />
        </section>

        {/* Antrian & pratinjau */}
        {items.length > 0 && (
          <section className="results-section">
            <QueueList
              items={items}
              selectedId={selectedId}
              onSelect={setSelectedId}
              onRemove={(id) => {
                remove(id);
                if (selectedId === id) setSelectedId(null);
              }}
              onClear={() => { clear(); setSelectedId(null); }}
            />

            {selectedItem?.markdown && (
              <SplitView
                markdown={selectedItem.markdown}
                filename={selectedItem.name}
              />
            )}
          </section>
        )}
      </main>

      {/* Toast notifications — FR-25, NFR-A3 */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
}
