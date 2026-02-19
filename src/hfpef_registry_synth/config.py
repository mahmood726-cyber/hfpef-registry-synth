"""Configuration objects and helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence


@dataclass
class PipelineConfig:
    """Runtime configuration for the HFpEF registry-first pipeline."""

    out_dir: Path = Path("outputs")
    cache_dir: Path = Path("cache")
    start_year: int = 2015
    grace_months: int = 24
    baseline_risks: List[int] = field(default_factory=lambda: [50, 100, 200])
    mnar_deltas: List[float] = field(default_factory=lambda: [0.0, 0.10, 0.20])
    use_pubmed: bool = False
    use_openalex: bool = False
    request_timeout: int = 30
    max_retries: int = 4
    sleep_seconds: float = 0.2
    clinically_meaningful_arr: float = 10.0

    def ensure_dirs(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


def parse_int_list(text: str, fallback: Sequence[int]) -> List[int]:
    if not text:
        return list(fallback)
    try:
        values = [int(x.strip()) for x in text.split(",") if x.strip()]
        return values or list(fallback)
    except ValueError:
        return list(fallback)


def parse_float_list(text: str, fallback: Sequence[float]) -> List[float]:
    if not text:
        return list(fallback)
    try:
        values = [float(x.strip()) for x in text.split(",") if x.strip()]
        return values or list(fallback)
    except ValueError:
        return list(fallback)


def parse_bool(text: str, default: bool = False) -> bool:
    if text is None:
        return default
    norm = text.strip().lower()
    if norm in {"1", "true", "t", "yes", "y"}:
        return True
    if norm in {"0", "false", "f", "no", "n"}:
        return False
    return default


def normalize_baseline_risks(risks: Iterable[int]) -> List[int]:
    out = sorted({int(r) for r in risks if int(r) > 0})
    return out or [50, 100, 200]
