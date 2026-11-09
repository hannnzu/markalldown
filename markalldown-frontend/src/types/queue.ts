// QueueItem store — sesuai SPEC-001 § Data Models / QueueItem
// Menggunakan Zustand untuk state management

export type QueueStatus = "pending" | "converting" | "success" | "error";
export type QueueKind = "file" | "url";

export interface QueueItem {
  id: string;
  kind: QueueKind;
  name: string;
  sizeBytes: number | null;
  status: QueueStatus;
  progress: number; // 0-100
  markdown: string | null;
  errorCode: string | null;
  errorMessage: string | null;
  warnings: string[];
  convertedAt: string | null;
}
