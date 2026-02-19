"""Text parsing and outcome harmonization utilities."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from statistics import median
from typing import Dict, Iterable, List, Optional

from .utils import normalize_ws

try:
    from rapidfuzz import fuzz  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    fuzz = None


HF_HOSP_TERMS = [
    "heart failure hospitalization",
    "hospitalization for heart failure",
    "hf hospitalization",
    "heart failure admission",
]

SAE_TERMS = [
    "serious adverse event",
    "serious adverse events",
    "sae",
    "serious ae",
]

EF_REGEX = re.compile(
    r"(?:lvef|left ventricular ejection fraction|ejection fraction|ef)[^\n\.;:]{0,50}?"
    r"(?P<op>>=|=>|≤|<=|>|<|=|at least|at most|greater than or equal to|less than or equal to|"
    r"greater than|less than)?\s*(?P<val>\d{1,2})\s*%",
    flags=re.IGNORECASE,
)


@dataclass
class EfParseResult:
    operator: str
    value: Optional[int]
    band: str


@dataclass
class OutcomeChoice:
    title: str
    time_frame: str
    time_months: Optional[float]
    source_idx: int


def _norm(text: str) -> str:
    return normalize_ws(text).lower()


def extract_ef_cutoff(texts: Iterable[str]) -> EfParseResult:
    joined = "\n".join(t for t in texts if t)
    best_val: Optional[int] = None
    best_op = "unknown"
    for match in EF_REGEX.finditer(joined):
        val = int(match.group("val"))
        op = _norm(match.group("op") or ">=")
        if best_val is None or val > best_val:
            best_val = val
            best_op = op

    if best_val is None:
        return EfParseResult(operator="unknown", value=None, band="unknown")

    band = "unknown"
    if best_val >= 50 and best_op in {">=", "=>", "at least", "greater than", "greater than or equal to", ">", "="}:
        band = "strict_hfpef"
    elif best_val >= 40:
        band = "mixed_or_midrange"
    return EfParseResult(operator=best_op, value=best_val, band=band)


def _fuzzy_contains(text: str, phrase: str, cutoff: int = 88) -> bool:
    if fuzz is None:
        return False
    return fuzz.partial_ratio(text, phrase) >= cutoff


def is_hf_hosp_outcome(text: str) -> bool:
    raw = _norm(text)
    if "heart failure" in raw and "hospital" in raw:
        return True
    for term in HF_HOSP_TERMS:
        if term in raw:
            return True
        if _fuzzy_contains(raw, term):
            return True
    return False


def is_sae_outcome(text: str) -> bool:
    raw = _norm(text)
    if "serious" in raw and ("adverse" in raw or "ae" in raw):
        return True
    for term in SAE_TERMS:
        if term in raw:
            return True
    return False


def parse_timeframe_months(text: str) -> Optional[float]:
    raw = _norm(text)
    if not raw:
        return None

    patterns = [
        (r"(\d+(?:\.\d+)?)\s*year", 12.0),
        (r"(\d+(?:\.\d+)?)\s*month", 1.0),
        (r"(\d+(?:\.\d+)?)\s*week", 1.0 / 4.345),
        (r"(\d+(?:\.\d+)?)\s*day", 1.0 / 30.4375),
    ]
    for pattern, mult in patterns:
        m = re.search(pattern, raw)
        if m:
            return float(m.group(1)) * mult

    # Handle ranges by taking upper bound when explicit numbers exist.
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", raw)]
    if nums:
        max_num = max(nums)
        if "year" in raw:
            return max_num * 12.0
        if "month" in raw:
            return max_num
        if "week" in raw:
            return max_num / 4.345
        if "day" in raw:
            return max_num / 30.4375
    return None


def choose_preferred_outcome(outcomes: List[Dict[str, str]], matcher) -> Optional[OutcomeChoice]:
    candidates: List[OutcomeChoice] = []
    for idx, out in enumerate(outcomes):
        title = normalize_ws(out.get("title", ""))
        desc = normalize_ws(out.get("description", ""))
        time_frame = normalize_ws(out.get("timeFrame", ""))
        text = " ".join([title, desc])
        if matcher(text):
            candidates.append(
                OutcomeChoice(
                    title=title,
                    time_frame=time_frame,
                    time_months=parse_timeframe_months(time_frame),
                    source_idx=idx,
                )
            )

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: (
            -9999.0 if x.time_months is None else -x.time_months,
            x.source_idx,
        )
    )
    return candidates[0]


def endpoint_alignment_flags(values: Iterable[Optional[float]], tolerance: float = 0.2) -> List[bool]:
    nums = [v for v in values if v is not None and not math.isnan(v)]
    if not nums:
        return []
    med = float(median(nums))
    out: List[bool] = []
    for v in values:
        if v is None:
            out.append(False)
            continue
        if med == 0:
            out.append(v == 0)
            continue
        out.append(abs(v - med) / med <= tolerance)
    return out
