"""Custom exceptions untuk markalldown-backend.

Format error konsisten dengan API_SPEC.md dan ApiError schema.
"""
from __future__ import annotations


class AppError(Exception):
    """Exception dasar yang dipetakan langsung ke JSON ApiError."""

    def __init__(self, status_code: int, error: str, message: str):
        self.status_code = status_code
        self.error = error
        self.message = message
        super().__init__(message)
