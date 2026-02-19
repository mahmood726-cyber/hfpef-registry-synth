"""General utility helpers."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from dateutil import parser as date_parser


def parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return date_parser.parse(value)
    except (ValueError, TypeError, OverflowError):
        return None


def extract_date_from_struct(data: Dict[str, Any]) -> Optional[datetime]:
    if not isinstance(data, dict):
        return None
    for key in ("date", "dateString", "value", "monthDayYear"):
        dt = parse_date(data.get(key))
        if dt:
            return dt
    return None


def year_from_date_struct(data: Dict[str, Any]) -> Optional[int]:
    dt = extract_date_from_struct(data)
    return dt.year if dt else None


def safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        text = str(value).strip()
        if not text:
            return None
        return float(text)
    except (ValueError, TypeError):
        return None


def safe_int(value: Any) -> Optional[int]:
    f = safe_float(value)
    if f is None:
        return None
    try:
        return int(round(f))
    except (ValueError, TypeError):
        return None


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def to_json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def unique_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
