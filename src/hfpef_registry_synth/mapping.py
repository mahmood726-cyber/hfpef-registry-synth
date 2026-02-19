"""Intervention and comparator mapping utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, Iterable, List, Optional, Tuple

from .utils import normalize_ws, unique_preserve_order

try:
    from rapidfuzz import fuzz  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    fuzz = None


CLASS_PATTERNS: Dict[str, List[str]] = {
    "SGLT2 inhibitors": [
        "empagliflozin",
        "dapagliflozin",
        "canagliflozin",
        "ertugliflozin",
        "sotagliflozin",
    ],
    "ARNI": ["sacubitril/valsartan", "valsartan/sacubitril", "sacubitril", "lcz696", "entresto"],
    "MRA": ["spironolactone", "eplerenone", "finerenone"],
    "ARB/ACEi": [
        "valsartan",
        "candesartan",
        "losartan",
        "irbesartan",
        "enalapril",
        "lisinopril",
        "ramipril",
        "perindopril",
    ],
    "sGC stimulators": ["vericiguat", "riociguat", "praliciguat"],
    "Neprilysin inhibitors": ["omapatrilat", "neprilysin inhibitor"],
    "Beta blockers": ["carvedilol", "metoprolol", "bisoprolol", "nebivolol"],
    "Other": [],
}

COMPARATOR_REGEX_PATTERNS = [
    r"\bplacebo\b",
    r"\bstandard of care\b",
    r"\busual care\b",
    r"\bcontrol(?: arm| group)?\b",
    r"\bsham\b",
    r"\bno treatment\b",
    r"\bsoc\b",
]

HFPEF_TERMS = [
    "hfpef",
    "heart failure with preserved ejection fraction",
    "preserved ejection fraction",
    "diastolic heart failure",
]


@dataclass
class ClassMatch:
    class_name: str
    canonical_term: str
    confidence: float


def _norm(text: str) -> str:
    return normalize_ws(text).lower()


def _fuzzy_score(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if fuzz is not None:
        return float(fuzz.partial_ratio(a, b))
    return 100.0 * SequenceMatcher(None, a, b).ratio()


def _is_placebo_or_soc(raw: str) -> bool:
    return any(re.search(pattern, raw) for pattern in COMPARATOR_REGEX_PATTERNS)


def classify_intervention(name: str, intervention_type: Optional[str] = None) -> ClassMatch:
    """Map intervention name to pre-specified class with fuzzy fallback."""
    raw = _norm(name)
    if not raw:
        return ClassMatch("Unknown", "", 0.0)

    if intervention_type and _norm(intervention_type) in {"placebo", "control", "sham comparator"}:
        return ClassMatch("Placebo/SoC", "placebo", 100.0)

    if _is_placebo_or_soc(raw):
        return ClassMatch("Placebo/SoC", "comparator_pattern", 100.0)

    best: Optional[ClassMatch] = None
    for class_name, terms in CLASS_PATTERNS.items():
        if class_name == "Other":
            continue
        for term in terms:
            if term in raw:
                return ClassMatch(class_name, term, 100.0)
            score = _fuzzy_score(raw, term)
            if best is None or score > best.confidence:
                best = ClassMatch(class_name, term, score)

    if best and best.confidence >= 83:
        return best

    return ClassMatch("Other", raw, best.confidence if best else 0.0)


def classify_comparator(name: str, intervention_type: Optional[str] = None) -> str:
    raw = _norm(name)
    if intervention_type and _norm(intervention_type) in {"placebo", "control", "sham comparator"}:
        return "Placebo/SoC"
    if _is_placebo_or_soc(raw):
        return "Placebo/SoC"
    match = classify_intervention(name, intervention_type)
    return match.class_name


def classify_many(names: Iterable[str]) -> List[str]:
    classes = [classify_intervention(name).class_name for name in names if name]
    return unique_preserve_order(classes)


def is_hfpef_targeted(text: str) -> bool:
    raw = _norm(text)
    return any(term in raw for term in HFPEF_TERMS)


def normalize_drug_label(name: str) -> str:
    text = _norm(name)
    text = re.sub(r"[^a-z0-9+/ ]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()[:80]
