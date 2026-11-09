"""URL Fetcher — SPEC-001 D-10: SSRF prevention, redirect hops, YouTube transcript.

Memenuhi:
- FR-9, FR-10, FR-11, FR-12
- AC-7, AC-8, AC-9, AC-10
- EC-9, EC-10, EC-11, EC-12
- NFR-S6: timeout 15 detik, batas 20 MB
"""
from __future__ import annotations

import ipaddress
import logging
import socket
from urllib.parse import parse_qs, urlparse

import httpx
from youtube_transcript_api import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    YouTubeTranscriptApi,
)
from youtube_transcript_api._errors import (
    IpBlocked,
    RequestBlocked,
)

from app.exceptions import AppError

logger = logging.getLogger(__name__)

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}
MAX_REDIRECTS = 5
MAX_URL_RESPONSE_BYTES = 20 * 1024 * 1024  # 20 MB (NFR-S6)
URL_TIMEOUT_SECONDS = 15.0  # 15 detik (NFR-S6)


def is_private_or_restricted_ip(ip_str: str) -> bool:
    """Mengecek apakah IP adalah loopback, privat, link-local, atau multicast."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False

    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def validate_url_ssrf(url: str) -> tuple[str, str]:
    """Validasi skema dan resolusi DNS untuk mencegah SSRF (FR-11, FR-12, AC-9, AC-10).

    Mengembalikan (scheme, hostname).
    """
    try:
        parsed = urlparse(url)
    except Exception as exc:
        raise AppError(
            status_code=400,
            error="URL_NOT_ALLOWED",
            message=f"Format URL tidak valid: {url}",
        ) from exc

    # AC-10: Skema hanya http dan https
    if parsed.scheme.lower() not in ("http", "https"):
        raise AppError(
            status_code=400,
            error="URL_NOT_ALLOWED",
            message=f"Skema '{parsed.scheme}' tidak diizinkan. Hanya http dan https yang didukung.",
        )

    hostname = (parsed.hostname or "").strip().lower()
    if not hostname:
        raise AppError(
            status_code=400,
            error="URL_NOT_ALLOWED",
            message="Host URL tidak boleh kosong.",
        )

    # Cek jika hostname langsung berupa IP (AC-9)
    if is_private_or_restricted_ip(hostname):
        raise AppError(
            status_code=400,
            error="URL_NOT_ALLOWED",
            message=f"Akses ke alamat IP privat '{hostname}' tidak diizinkan.",
        )

    # Resolve DNS dan periksa semua IP hasil resolusi
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for res in addr_info:
            sockaddr = res[4]
            ip_str = sockaddr[0]
            if is_private_or_restricted_ip(ip_str):
                raise AppError(
                    status_code=400,
                    error="URL_NOT_ALLOWED",
                    message=f"Host '{hostname}' mengarah ke alamat IP privat/lokal ({ip_str}).",
                )
    except AppError:
        raise
    except Exception as exc:
        raise AppError(
            status_code=502,
            error="URL_FETCH_FAILED",
            message=f"Gagal menyelesaikan DNS untuk domain '{hostname}'.",
        ) from exc

    return parsed.scheme.lower(), hostname


def is_youtube_url(url: str) -> bool:
    """Mendeteksi apakah URL berasal dari domain YouTube yang diizinkan (D-10)."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    return host in YOUTUBE_HOSTS


def extract_youtube_video_id(url: str) -> str | None:
    """Ekstraksi ID video YouTube dari berbagai format URL."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()

    if host == "youtu.be":
        return parsed.path.lstrip("/").split("/")[0] or None

    if host in ("youtube.com", "www.youtube.com", "m.youtube.com"):
        if parsed.path.startswith("/watch"):
            qs = parse_qs(parsed.query)
            return qs.get("v", [None])[0]
        if parsed.path.startswith("/shorts/"):
            parts = [p for p in parsed.path.split("/") if p]
            return parts[1] if len(parts) > 1 else None

    return None


async def fetch_web_content(url: str) -> tuple[bytes, str]:
    """Mengambil konten halaman web secara aman dengan pembatasan SSRF dan redirect hops (D-10)."""
    current_url = url

    async with httpx.AsyncClient(timeout=URL_TIMEOUT_SECONDS) as client:
        for _ in range(MAX_REDIRECTS):
            validate_url_ssrf(current_url)

            try:
                resp = await client.get(current_url, follow_redirects=False)
            except (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError) as exc:
                logger.warning("Gagal fetch %s: %s", current_url, exc)
                raise AppError(
                    status_code=502,
                    error="URL_FETCH_FAILED",
                    message=f"Gagal menjangkau URL: {current_url}",
                ) from exc

            # Validasi per-hop redirect (EC-10)
            if resp.is_redirect:
                loc = resp.headers.get("location")
                if not loc:
                    break
                redirect_url = str(httpx.URL(current_url).join(loc))
                validate_url_ssrf(redirect_url)
                current_url = redirect_url
            else:
                if resp.status_code >= 400:
                    raise AppError(
                        status_code=502,
                        error="URL_FETCH_FAILED",
                        message=f"URL mengembalikan respons error HTTP {resp.status_code}.",
                    )

                content = resp.content
                if len(content) > MAX_URL_RESPONSE_BYTES:
                    raise AppError(
                        status_code=502,
                        error="URL_FETCH_FAILED",
                        message="Ukuran konten halaman web melebihi batas 20 MB.",
                    )
                return content, current_url

    raise AppError(
        status_code=502,
        error="URL_FETCH_FAILED",
        message="Terlalu banyak pengalihan (redirect loop).",
    )


def get_youtube_transcript_raw(video_id: str) -> list[str]:
    """Helper fungsi pemanggil API YouTube transcript agar mudah diuji/dimock."""
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)
    return [part.text for part in transcript]


def fetch_youtube_transcript(url: str) -> str:
    """Mengambil transkrip video YouTube menggunakan youtube_transcript_api (FR-10, EC-11, EC-12)."""
    video_id = extract_youtube_video_id(url)
    if not video_id:
        raise AppError(
            status_code=422,
            error="TRANSCRIPT_UNAVAILABLE",
            message="ID video YouTube tidak ditemukan dalam URL.",
        )

    try:
        lines = get_youtube_transcript_raw(video_id)
        text_content = "\n".join(lines).strip()
        if not text_content:
            raise AppError(
                status_code=422,
                error="TRANSCRIPT_UNAVAILABLE",
                message="Transkrip kosong untuk video ini.",
            )
        return f"# YouTube Video Transcript ({video_id})\n\n{text_content}"

    except AppError:
        raise
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
        raise AppError(
            status_code=422,
            error="TRANSCRIPT_UNAVAILABLE",
            message="Transkrip tidak tersedia untuk video ini atau video bersifat privat.",
        )
    except (IpBlocked, RequestBlocked):
        raise AppError(
            status_code=503,
            error="UPSTREAM_THROTTLED",
            message="YouTube membatasi laju permintaan (throttled). Coba lagi nanti.",
        )
    except CouldNotRetrieveTranscript as exc:
        err_msg = str(exc).lower()
        if "too many requests" in err_msg or "rate" in err_msg or "blocked" in err_msg or "throttled" in err_msg:
            raise AppError(
                status_code=503,
                error="UPSTREAM_THROTTLED",
                message="YouTube membatasi laju permintaan (throttled). Coba lagi nanti.",
            ) from exc
        raise AppError(
            status_code=422,
            error="TRANSCRIPT_UNAVAILABLE",
            message="Transkrip tidak dapat diambil untuk video ini.",
        ) from exc
    except Exception as exc:
        err_str = str(exc).lower()
        if "blocked" in err_str or "throttle" in err_str:
            raise AppError(
                status_code=503,
                error="UPSTREAM_THROTTLED",
                message="YouTube membatasi laju permintaan (throttled). Coba lagi nanti.",
            ) from exc
        logger.warning("YouTube transcript fetch error for %s: %s", url, exc)
        raise AppError(
            status_code=422,
            error="TRANSCRIPT_UNAVAILABLE",
            message=f"Transkrip tidak tersedia: {exc}",
        ) from exc
