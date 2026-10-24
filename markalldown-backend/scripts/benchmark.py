"""Benchmark conversion performance — SPEC-001 D-3 / NFR-P2.

Measures conversion time of a ~5 MB document across multiple runs, calculating p95.
"""
from __future__ import annotations

import io
import time

import numpy as np
from markitdown import MarkItDown, StreamInfo


def generate_5mb_docx() -> bytes:
    from docx import Document
    doc = Document()
    doc.add_heading("Benchmark Document", 0)
    # Add repeated text to reach ~4.5-5MB
    sample_text = ("The quick brown fox jumps over the lazy dog. " * 20) + "\n"
    for i in range(500):
        doc.add_paragraph(f"Section {i}: " + sample_text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def run_benchmark(num_runs: int = 5) -> float:
    print("Generating test DOCX...", flush=True)
    data = generate_5mb_docx()
    size_mb = len(data) / (1024 * 1024)
    print(f"Generated DOCX size: {size_mb:.2f} MB", flush=True)

    md = MarkItDown()
    times = []

    print(f"Executing {num_runs} conversion runs...", flush=True)
    for i in range(num_runs):
        t0 = time.perf_counter()
        stream = io.BytesIO(data)
        res = md.convert_stream(stream, stream_info=StreamInfo(extension=".docx", filename="benchmark.docx"))
        elapsed = time.perf_counter() - t0
        times.append(elapsed)
        print(f"  Run {i+1:02d}: {elapsed:.3f}s (output len: {len(res.text_content)})", flush=True)

    p95 = float(np.percentile(times, 95))
    p50 = float(np.percentile(times, 50))
    print("\n--- Benchmark Results ---", flush=True)
    print(f"Median (p50): {p50:.3f}s", flush=True)
    print(f"p95:          {p95:.3f}s (Target NFR-P2: < 15.000s)", flush=True)
    return p95


if __name__ == "__main__":
    run_benchmark(num_runs=5)
