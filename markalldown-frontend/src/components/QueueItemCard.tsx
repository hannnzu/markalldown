"use client";

import type { QueueItem } from "@/types/queue";

interface QueueItemCardProps {
  item: QueueItem;
  selected: boolean;
  onSelect: () => void;
  onRemove: () => void;
  onDownload: () => void;
}

const STATUS_LABEL: Record<string, string> = {
  pending: "Menunggu",
  converting: "Mengonversi…",
  success: "Berhasil",
  error: "Gagal",
};

export default function QueueItemCard({
  item,
  selected,
  onSelect,
  onRemove,
  onDownload,
}: QueueItemCardProps) {
  const isSuccess = item.status === "success";
  const isError = item.status === "error";
  const isConverting = item.status === "converting";

  return (
    <div
      className={`queue-item queue-item--${item.status} ${selected ? "queue-item--selected" : ""}`}
      role="listitem"
      aria-label={`${item.name} — ${STATUS_LABEL[item.status]}`}
    >
      <div className="queue-item__header">
        <span className="queue-item__icon" aria-hidden="true">
          {item.kind === "url" ? "🔗" : "📄"}
        </span>
        <div className="queue-item__info">
          <span className="queue-item__name" title={item.name}>
            {item.name}
          </span>
          {item.sizeBytes !== null && (
            <span className="queue-item__size">
              {(item.sizeBytes / 1024 / 1024).toFixed(2)} MB
            </span>
          )}
        </div>
        <span
          className={`queue-item__badge queue-item__badge--${item.status}`}
          aria-live="polite"
        >
          {STATUS_LABEL[item.status]}
        </span>
      </div>

      {/* Progress bar — AC-17, FR-24 */}
      <div className="queue-item__progress-track" role="progressbar" aria-valuenow={item.progress} aria-valuemin={0} aria-valuemax={100}>
        <div
          className={`queue-item__progress-fill ${isConverting ? "queue-item__progress-fill--indeterminate" : ""}`}
          style={!isConverting ? { width: `${item.progress}%` } : undefined}
        />
      </div>

      {/* Pesan error — AC-28 */}
      {isError && item.errorMessage && (
        <p className="queue-item__error" aria-live="assertive">
          {item.errorMessage}
        </p>
      )}

      {/* Peringatan */}
      {isSuccess && item.warnings.length > 0 && (
        <p className="queue-item__warning">
          ⚠️ {item.warnings.join(", ")}
        </p>
      )}

      <div className="queue-item__actions">
        {isSuccess && (
          <>
            <button className="btn btn--ghost btn--sm" onClick={onSelect}>
              {selected ? "Sembunyikan pratinjau" : "Pratinjau"}
            </button>
            <button className="btn btn--ghost btn--sm" onClick={onDownload}>
              Unduh .md
            </button>
          </>
        )}
        <button
          className="btn btn--ghost btn--sm btn--danger"
          onClick={onRemove}
          aria-label={`Hapus ${item.name} dari antrean`}
        >
          Hapus
        </button>
      </div>
    </div>
  );
}
