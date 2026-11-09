import { create } from "zustand";
import type { QueueItem, QueueStatus } from "@/types/queue";

// Polyfill uuid karena crypto.randomUUID tersedia di browser modern
const newId = () =>
  typeof crypto !== "undefined" && crypto.randomUUID
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2);

interface QueueStore {
  items: QueueItem[];
  addFile: (file: File) => string;
  addUrl: (url: string) => string;
  setStatus: (id: string, status: QueueStatus) => void;
  setProgress: (id: string, progress: number) => void;
  setSuccess: (
    id: string,
    markdown: string,
    convertedAt: string,
    warnings?: string[]
  ) => void;
  setError: (id: string, errorCode: string, errorMessage: string) => void;
  remove: (id: string) => void;
  clear: () => void;
}

export const useQueueStore = create<QueueStore>((set) => ({
  items: [],

  addFile: (file) => {
    const id = newId();
    set((s) => ({
      items: [
        ...s.items,
        {
          id,
          kind: "file",
          name: file.name,
          sizeBytes: file.size,
          status: "pending",
          progress: 0,
          markdown: null,
          errorCode: null,
          errorMessage: null,
          warnings: [],
          convertedAt: null,
        },
      ],
    }));
    return id;
  },

  addUrl: (url) => {
    const id = newId();
    set((s) => ({
      items: [
        ...s.items,
        {
          id,
          kind: "url",
          name: url,
          sizeBytes: null,
          status: "pending",
          progress: 0,
          markdown: null,
          errorCode: null,
          errorMessage: null,
          warnings: [],
          convertedAt: null,
        },
      ],
    }));
    return id;
  },

  setStatus: (id, status) =>
    set((s) => ({
      items: s.items.map((item) =>
        item.id === id ? { ...item, status } : item
      ),
    })),

  setProgress: (id, progress) =>
    set((s) => ({
      items: s.items.map((item) =>
        item.id === id ? { ...item, progress } : item
      ),
    })),

  setSuccess: (id, markdown, convertedAt, warnings = []) =>
    set((s) => ({
      items: s.items.map((item) =>
        item.id === id
          ? { ...item, status: "success", progress: 100, markdown, convertedAt, warnings }
          : item
      ),
    })),

  setError: (id, errorCode, errorMessage) =>
    set((s) => ({
      items: s.items.map((item) =>
        item.id === id
          ? { ...item, status: "error", errorCode, errorMessage }
          : item
      ),
    })),

  remove: (id) =>
    set((s) => ({ items: s.items.filter((item) => item.id !== id) })),

  clear: () => set({ items: [] }),
}));
