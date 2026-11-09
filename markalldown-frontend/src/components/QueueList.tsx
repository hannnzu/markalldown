"use client";

import { useCallback } from "react";
import JSZip from "jszip";
import type { QueueItem } from "@/types/queue";
import QueueItemCard from "./QueueItemCard";

interface QueueListProps {
  items: QueueItem[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  onRemove: (id: string) => void;
  onClear: () => void;
}

function downloadFile(filename: string, content: string) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function toMdFilename(name: string): string {
  // Ganti ekstensi terakhir dengan .md — AC-19
  const dot = name.lastIndexOf(".");
  return (dot > 0 ? name.slice(0, dot) : name) + ".md";
}

export default function QueueList({
  items,
  selectedId,
  onSelect,
  onRemove,
  onClear,
}: QueueListProps) {
  const successItems = items.filter((i) => i.status === "success");

  // Unduh semua hasil sukses sebagai ZIP — FR-22, AC-20, D-6 (ZIP dibuat di klien)
  const downloadAll = useCallback(async () => {
    if (successItems.length === 0) return;
    const zip = new JSZip();
    const seen: Record<string, number> = {};
    for (const item of successItems) {
      let fname = toMdFilename(item.name);
      if (seen[fname] !== undefined) {
        seen[fname]++;
        const dot = fname.lastIndexOf(".");
        fname = `${fname.slice(0, dot)}-${seen[fname]}${fname.slice(dot)}`;
      } else {
        seen[fname] = 0;
      }
      zip.file(fname, item.markdown ?? "");
    }
    const blob = await zip.generateAsync({ type: "blob" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "markalldown-batch.zip";
    a.click();
    URL.revokeObjectURL(url);
  }, [successItems]);

  if (items.length === 0) return null;

  return (
    <section className="queue-list" aria-label="Antrean konversi">
      <div className="queue-list__header">
        <h2 className="queue-list__title">
          Antrean ({items.length})
        </h2>
        <div className="queue-list__actions">
          {successItems.length > 1 && (
            <button className="btn btn--primary btn--sm" onClick={downloadAll}>
              Unduh semua ({successItems.length}) sebagai ZIP
            </button>
          )}
          <button className="btn btn--ghost btn--sm btn--danger" onClick={onClear}>
            Bersihkan semua
          </button>
        </div>
      </div>

      <div role="list" className="queue-list__items">
        {items.map((item) => (
          <QueueItemCard
            key={item.id}
            item={item}
            selected={selectedId === item.id}
            onSelect={() => onSelect(selectedId === item.id ? null : item.id)}
            onRemove={() => onRemove(item.id)}
            onDownload={() =>
              item.markdown && downloadFile(toMdFilename(item.name), item.markdown)
            }
          />
        ))}
      </div>
    </section>
  );
}
