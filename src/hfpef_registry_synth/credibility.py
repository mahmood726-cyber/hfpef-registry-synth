"""External face-validity checks against known HFpEF class-level signals."""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


EXPECTED_SIGNALS: List[Dict[str, str]] = [
    {
        "outcome": "HF_HOSPITALIZATION",
        "intervention_class": "SGLT2 inhibitors",
        "expected_direction": "benefit",
        "anchor_reference": "EMPEROR-Preserved (NCT03057951) and DELIVER (NCT03619213): reduced HF hospitalization-driven composite risk.",
    },
    {
        "outcome": "HF_HOSPITALIZATION",
        "intervention_class": "ARNI",
        "expected_direction": "uncertain_or_small_benefit",
        "anchor_reference": "PARAGON-HF (NCT01920711): near-neutral primary result with subgroup-sensitive signal.",
    },
    {
        "outcome": "HF_HOSPITALIZATION",
        "intervention_class": "MRA",
        "expected_direction": "uncertain_or_small_benefit",
        "anchor_reference": "TOPCAT (NCT00094302): mixed signal and regional heterogeneity concerns.",
    },
    {
        "outcome": "SAE",
        "intervention_class": "SGLT2 inhibitors",
        "expected_direction": "neutral_or_benefit",
        "anchor_reference": "Major HFpEF SGLT2 RCTs generally do not show excess overall serious adverse events.",
    },
]


def _observed_direction(ci_low_rr: float, ci_high_rr: float) -> str:
    if ci_high_rr < 1.0:
        return "benefit"
    if ci_low_rr > 1.0:
        return "harm"
    return "uncertain"


def _concordance(expected: str, observed: str, rr: float) -> str:
    if expected == "benefit":
        if observed == "benefit":
            return "full_concordance"
        if observed == "uncertain" and rr < 1.0:
            return "partial_concordance"
        return "discordant"
    if expected in {"uncertain_or_small_benefit", "neutral_or_benefit"}:
        if observed == "uncertain":
            return "full_concordance"
        if observed == "benefit":
            return "partial_concordance"
        return "discordant"
    if expected == "harm":
        if observed == "harm":
            return "full_concordance"
        if observed == "uncertain" and rr > 1.0:
            return "partial_concordance"
        return "discordant"
    return "not_evaluable"


def run_external_credibility_checks(hfhosp_summary: pd.DataFrame, sae_summary: pd.DataFrame) -> pd.DataFrame:
    lookup = {}
    if not hfhosp_summary.empty:
        for _, row in hfhosp_summary.iterrows():
            lookup[(str(row.get("intervention_class", "")), "HF_HOSPITALIZATION")] = row
    if not sae_summary.empty:
        for _, row in sae_summary.iterrows():
            lookup[(str(row.get("intervention_class", "")), "SAE")] = row

    rows: List[Dict[str, Any]] = []
    for anchor in EXPECTED_SIGNALS:
        cls = anchor["intervention_class"]
        outcome = anchor["outcome"]
        srow = lookup.get((cls, outcome))
        if srow is None:
            rows.append(
                {
                    "intervention_class": cls,
                    "outcome": outcome,
                    "expected_direction": anchor["expected_direction"],
                    "observed_direction": "not_estimated",
                    "concordance": "not_evaluable",
                    "pooled_rr": float("nan"),
                    "ci_low_rr": float("nan"),
                    "ci_high_rr": float("nan"),
                    "anchor_reference": anchor["anchor_reference"],
                }
            )
            continue

        rr = float(srow.get("pooled_rr"))
        ci_low = float(srow.get("ci_low_rr"))
        ci_high = float(srow.get("ci_high_rr"))
        observed = _observed_direction(ci_low, ci_high)
        conc = _concordance(anchor["expected_direction"], observed, rr)
        rows.append(
            {
                "intervention_class": cls,
                "outcome": outcome,
                "expected_direction": anchor["expected_direction"],
                "observed_direction": observed,
                "concordance": conc,
                "pooled_rr": rr,
                "ci_low_rr": ci_low,
                "ci_high_rr": ci_high,
                "anchor_reference": anchor["anchor_reference"],
            }
        )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["outcome", "intervention_class"]).reset_index(drop=True)
    return out
