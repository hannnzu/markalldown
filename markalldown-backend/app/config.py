"""AppConfig — dibaca dari environment / .env (pydantic-settings).

Semua nilai default adalah untuk development. Produksi wajib override
ENVIRONMENT, ALLOWED_ORIGINS (tanpa *), dan SUPABASE_* via env Railway.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Deployment
    ENVIRONMENT: str = "development"

    # CORS — AC-12: tidak boleh "*" di production
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # Batas file
    MAX_FILE_SIZE_MB: int = 50
    MAX_BATCH_SIZE_MB: int = 100

    # Rate limit (default fallback in-memory; Supabase dipakai jika tersedia)
    RATE_LIMIT_PER_MIN: int = 30

    # Supabase — rate limiting terpusat (D-4 revisi, opsional)
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Versi app (dibaca saat startup)
    APP_VERSION: str = "0.1.0"

    @field_validator("MAX_BATCH_SIZE_MB")
    @classmethod
    def batch_gte_file(cls, v: int, info) -> int:
        max_file = info.data.get("MAX_FILE_SIZE_MB", 50)
        if v < max_file:
            raise ValueError(
                f"MAX_BATCH_SIZE_MB ({v}) must be >= MAX_FILE_SIZE_MB ({max_file})"
            )
        return v

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def max_batch_size_bytes(self) -> int:
        return self.MAX_BATCH_SIZE_MB * 1024 * 1024

    @property
    def supabase_configured(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_SERVICE_ROLE_KEY)


@lru_cache
def get_config() -> AppConfig:
    return AppConfig()
