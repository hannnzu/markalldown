// API Types — sesuai SPEC-001 § API Contracts

export interface ApiError {
  error: string;
  message: string;
}

export type ErrorCode =
  | "UNSUPPORTED_FILE_TYPE"
  | "FILE_TOO_LARGE"
  | "EMPTY_FILE"
  | "INVALID_FILE_CONTENT"
  | "ARCHIVE_CONTENT_NOT_ALLOWED"
  | "BATCH_TOO_LARGE"
  | "NO_FILES"
  | "TOO_MANY_FILES"
  | "ARCHIVE_LIMIT_EXCEEDED"
  | "TRANSCRIPT_UNAVAILABLE"
  | "URL_NOT_ALLOWED"
  | "RATE_LIMITED"
  | "URL_FETCH_FAILED"
  | "UPSTREAM_THROTTLED"
  | "CONVERSION_TIMEOUT"
  | "CONVERSION_FAILED"
  | "INTERNAL_ERROR";

export interface HealthResponse {
  status: "ok";
  version: string;
}

export interface ConvertFileResponse {
  filename: string;
  markdown: string;
  size_bytes: number;
  converted_at: string;
  warnings: string[];
}

export interface BatchItem {
  filename: string;
  markdown: string | null;
  status: "success" | "error";
  error?: string;
  message?: string;
}

export interface ConvertFilesResponse {
  results: BatchItem[];
  total: number;
  success: number;
  failed: number;
}

export interface ConvertUrlRequest {
  url: string;
}

export interface ConvertUrlResponse {
  source_url: string;
  markdown: string;
  converted_at: string;
}
