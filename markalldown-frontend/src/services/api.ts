import axios from "axios";
import type {
  ConvertFileResponse,
  ConvertFilesResponse,
  ConvertUrlResponse,
  HealthResponse,
} from "@/types/api";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const api = {
  health: (): Promise<HealthResponse> =>
    axios.get(`${BASE_URL}/api/health`).then((r) => r.data),

  /** Konversi satu file — FR-1 */
  convertFile: (
    file: File,
    onUploadProgress?: (pct: number) => void
  ): Promise<ConvertFileResponse> => {
    const form = new FormData();
    form.append("file", file);
    return axios
      .post(`${BASE_URL}/api/convert/file`, form, {
        onUploadProgress: (e) => {
          if (onUploadProgress && e.total) {
            onUploadProgress(Math.round((e.loaded / e.total) * 100));
          }
        },
      })
      .then((r) => r.data);
  },

  /** Konversi batch file — FR-2 */
  convertFiles: (
    files: File[],
    onUploadProgress?: (pct: number) => void
  ): Promise<ConvertFilesResponse> => {
    const form = new FormData();
    files.forEach((f) => form.append("files", f));
    return axios
      .post(`${BASE_URL}/api/convert/files`, form, {
        onUploadProgress: (e) => {
          if (onUploadProgress && e.total) {
            onUploadProgress(Math.round((e.loaded / e.total) * 100));
          }
        },
      })
      .then((r) => r.data);
  },

  /** Konversi URL / YouTube — FR-9, FR-10 */
  convertUrl: (url: string): Promise<ConvertUrlResponse> =>
    axios
      .post(`${BASE_URL}/api/convert/url`, { url })
      .then((r) => r.data),
};
