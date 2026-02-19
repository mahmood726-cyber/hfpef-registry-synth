"""Manual adjudication support and extraction validation metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from .ctgov_client import ctgov_record_url
from .parsing import choose_preferred_outcome, is_hf_hosp_outcome, is_sae_outcome, parse_timeframe_months
from .utils import normalize_ws


DOMAIN_SPECS = {
    "HF_HOSPITALIZATION": is_hf_hosp_outcome,
    "SAE": is_sae_outcome,
}


@dataclass
class ValidationOutputs:
    candidates_df: pd.DataFrame
    sample_df: pd.DataFrame
    metrics_df: pd.DataFrame
    misclassified_df: pd.DataFrame


def _nct_id(study: Dict[str, Any]) -> str:
    return (
        study.get("protocolSection", {})
        .get("identificationModule", {})
        .get("nctId", "")
        .upper()
    )


def _brief_title(study: Dict[str, Any]) -> str:
    return normalize_ws(
        study.get("protocolSection", {})
        .get("identificationModule", {})
        .get("briefTitle", "")
    )


def _result_outcomes(study: Dict[str, Any]) -> List[Dict[str, Any]]:
    return (
        study.get("resultsSection", {})
        .get("outcomeMeasuresModule", {})
        .get("outcomeMeasures", [])
        or []
    )


def build_outcome_validation_candidates(studies: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for nct_id, study in studies.items():
        outcomes = _result_outcomes(study)
        if not outcomes:
            continue

        brief = [
            {
                "title": normalize_ws(o.get("title", "")),
                "description": normalize_ws(o.get("description", "")),
                "timeFrame": normalize_ws(o.get("timeFrame", "")),
            }
            for o in outcomes
        ]
        preferred: Dict[str, Optional[int]] = {}
        for domain, matcher in DOMAIN_SPECS.items():
            chosen = choose_preferred_outcome(brief, matcher)
            preferred[domain] = chosen.source_idx if chosen is not None else None

        for idx, out in enumerate(brief):
            title = out.get("title", "")
            description = out.get("description", "")
            time_frame = out.get("timeFrame", "")
            text = normalize_ws(f"{title} {description}")
            for domain, matcher in DOMAIN_SPECS.items():
                match = bool(matcher(text))
                rows.append(
                    {
                        "nct_id": nct_id,
                        "brief_title": _brief_title(study),
                        "outcome_idx": idx,
                        "domain": domain,
                        "outcome_title": title,
                        "outcome_description": description,
                        "time_frame": time_frame,
                        "time_months": parse_timeframe_months(time_frame),
                        "algorithm_match": match,
                        "algorithm_selected": bool(match and preferred.get(domain) == idx),
                        "source_url": ctgov_record_url(nct_id),
                    }
                )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["domain", "nct_id", "outcome_idx"]).reset_index(drop=True)
    return out


def _sample_per_domain(df: pd.DataFrame, per_domain: int, seed: int) -> pd.DataFrame:
    if df.empty or per_domain <= 0:
        return pd.DataFrame(columns=df.columns if not df.empty else None)
    rng = np.random.default_rng(seed)
    samples: List[pd.DataFrame] = []

    for domain, dfd in df.groupby("domain"):
        pos = dfd[dfd["algorithm_selected"]]
        neg = dfd[~dfd["algorithm_selected"]]
        half = max(1, per_domain // 2)

        n_pos = min(len(pos), half)
        n_neg = min(len(neg), per_domain - n_pos)
        if n_neg < (per_domain - n_pos):
            n_pos = min(len(pos), per_domain - n_neg)

        pos_idx = rng.choice(pos.index.to_numpy(), size=n_pos, replace=False) if n_pos > 0 else np.array([], dtype=int)
        neg_idx = rng.choice(neg.index.to_numpy(), size=n_neg, replace=False) if n_neg > 0 else np.array([], dtype=int)
        picked_idx = np.concatenate([pos_idx, neg_idx]).astype(int)
        picked = dfd.loc[picked_idx].copy() if picked_idx.size else dfd.iloc[:0].copy()
        picked["sample_domain_target"] = per_domain
        picked["sample_seed"] = seed
        samples.append(picked)

    out = pd.concat(samples, ignore_index=True) if samples else pd.DataFrame(columns=df.columns)
    if out.empty:
        return out

    out = out.sort_values(["domain", "algorithm_selected"], ascending=[True, False]).reset_index(drop=True)
    out["sample_id"] = [f"SMP-{i+1:04d}" for i in range(len(out))]
    out["reviewer1_include"] = ""
    out["reviewer2_include"] = ""
    out["consensus_include"] = ""
    out["adjudication_notes"] = ""
    return out


def build_adjudication_sample(candidates_df: pd.DataFrame, per_domain: int, seed: int) -> pd.DataFrame:
    return _sample_per_domain(candidates_df, per_domain=per_domain, seed=seed)


def _safe_rate(num: float, den: float) -> float:
    if den <= 0:
        return np.nan
    return float(num) / float(den)


def compute_adjudication_metrics(
    adjudication_df: pd.DataFrame,
    candidates_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Compute misclassification rates from manual consensus labels.

    Expected adjudication columns:
    - domain
    - nct_id
    - outcome_idx
    - consensus_include (0/1/true/false style)
    """
    if adjudication_df.empty or candidates_df.empty:
        empty = pd.DataFrame()
        return empty, empty

    required = {"domain", "nct_id", "outcome_idx", "consensus_include"}
    missing = required - set(adjudication_df.columns)
    if missing:
        raise ValueError(f"Adjudication file missing columns: {sorted(missing)}")

    adjud = adjudication_df.copy()
    adjud["domain"] = adjud["domain"].astype(str)
    adjud["nct_id"] = adjud["nct_id"].astype(str).str.upper()
    adjud["outcome_idx"] = pd.to_numeric(adjud["outcome_idx"], errors="coerce")
    adjud = adjud[adjud["outcome_idx"].notna()].copy()
    adjud["outcome_idx"] = adjud["outcome_idx"].astype(int)
    if "algorithm_selected" in adjud.columns:
        adjud = adjud.drop(columns=["algorithm_selected"])

    consensus = adjud["consensus_include"].astype(str).str.strip().str.lower()
    consensus_map = {
        "1": True,
        "0": False,
        "true": True,
        "false": False,
        "yes": True,
        "no": False,
        "y": True,
        "n": False,
    }
    adjud["consensus_include_bool"] = consensus.map(consensus_map)
    adjud = adjud[adjud["consensus_include_bool"].notna()].copy()
    if adjud.empty:
        empty = pd.DataFrame()
        return empty, empty

    keys = ["domain", "nct_id", "outcome_idx"]
    merged = adjud.merge(
        candidates_df[keys + ["algorithm_selected", "outcome_title", "time_frame", "source_url"]],
        on=keys,
        how="left",
    )
    merged = merged[merged["algorithm_selected"].notna()].copy()
    if merged.empty:
        empty = pd.DataFrame()
        return empty, empty

    merged["algorithm_selected_bool"] = merged["algorithm_selected"].astype(bool)
    merged["tp"] = merged["algorithm_selected_bool"] & merged["consensus_include_bool"]
    merged["fp"] = merged["algorithm_selected_bool"] & (~merged["consensus_include_bool"])
    merged["tn"] = (~merged["algorithm_selected_bool"]) & (~merged["consensus_include_bool"])
    merged["fn"] = (~merged["algorithm_selected_bool"]) & merged["consensus_include_bool"]

    summary_rows: List[Dict[str, Any]] = []
    for domain, g in merged.groupby("domain"):
        tp = int(g["tp"].sum())
        fp = int(g["fp"].sum())
        tn = int(g["tn"].sum())
        fn = int(g["fn"].sum())
        n = int(len(g))
        summary_rows.append(
            {
                "domain": domain,
                "n_reviewed": n,
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "accuracy": _safe_rate(tp + tn, n),
                "sensitivity": _safe_rate(tp, tp + fn),
                "specificity": _safe_rate(tn, tn + fp),
                "ppv": _safe_rate(tp, tp + fp),
                "npv": _safe_rate(tn, tn + fn),
                "misclassification_rate": _safe_rate(fp + fn, n),
            }
        )

    metrics_df = pd.DataFrame(summary_rows).sort_values("domain").reset_index(drop=True)
    misclassified_df = merged[(merged["fp"]) | (merged["fn"])].copy()
    if not misclassified_df.empty:
        misclassified_df["error_type"] = np.where(misclassified_df["fp"], "false_positive", "false_negative")
        misclassified_df = misclassified_df[
            [
                "domain",
                "nct_id",
                "outcome_idx",
                "outcome_title",
                "time_frame",
                "algorithm_selected_bool",
                "consensus_include_bool",
                "error_type",
                "source_url",
            ]
        ].sort_values(["domain", "nct_id", "outcome_idx"])

    return metrics_df, misclassified_df


def build_validation_outputs(
    studies: Dict[str, Dict[str, Any]],
    sample_size_per_domain: int,
    seed: int,
    adjudication_df: Optional[pd.DataFrame] = None,
) -> ValidationOutputs:
    candidates_df = build_outcome_validation_candidates(studies)
    sample_df = build_adjudication_sample(candidates_df, per_domain=sample_size_per_domain, seed=seed)

    if adjudication_df is None:
        metrics_df = pd.DataFrame(
            [
                {
                    "domain": domain,
                    "n_reviewed": 0,
                    "tp": 0,
                    "fp": 0,
                    "tn": 0,
                    "fn": 0,
                    "accuracy": np.nan,
                    "sensitivity": np.nan,
                    "specificity": np.nan,
                    "ppv": np.nan,
                    "npv": np.nan,
                    "misclassification_rate": np.nan,
                    "status": "pending_manual_adjudication",
                }
                for domain in DOMAIN_SPECS
            ]
        )
        misclassified_df = pd.DataFrame()
    else:
        metrics_df, misclassified_df = compute_adjudication_metrics(adjudication_df, candidates_df)
        if not metrics_df.empty and "status" not in metrics_df.columns:
            metrics_df = metrics_df.assign(status="scored_from_consensus_labels")

    return ValidationOutputs(
        candidates_df=candidates_df,
        sample_df=sample_df,
        metrics_df=metrics_df,
        misclassified_df=misclassified_df,
    )
