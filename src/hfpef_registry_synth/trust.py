"""Transparency and trust capsule calculations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

from .utils import parse_date


def _class_completed_universe(universe_df: pd.DataFrame, cls: str) -> pd.DataFrame:
    df = universe_df.copy()
    return df[
        (df["primary_intervention_class"] == cls)
        & (df["overall_status"].str.upper() == "COMPLETED")
    ]


def _participant_sum(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    vals = pd.to_numeric(df["enrollment"], errors="coerce").fillna(0)
    return float(vals.sum())


def _reporting_debt_rate(class_completed: pd.DataFrame, grace_months: int, now: Optional[datetime] = None) -> float:
    if class_completed.empty:
        return 0.0

    now = now or datetime.now(timezone.utc)
    if now.tzinfo is not None:
        now = now.astimezone(timezone.utc).replace(tzinfo=None)
    older_mask = []
    for dt in class_completed["primary_completion_date"].tolist():
        parsed = parse_date(dt)
        older_mask.append(bool(parsed and parsed + relativedelta(months=grace_months) <= now))

    if not any(older_mask):
        return 0.0

    older_df = class_completed[pd.Series(older_mask, index=class_completed.index)]
    if older_df.empty:
        return 0.0

    has_pub = older_df.get("has_publication_link", pd.Series([False] * len(older_df), index=older_df.index)).astype(bool)
    has_results = older_df["results_posted"].astype(bool)
    unreported = (~has_results) & (~has_pub)
    return float(unreported.mean())


def _endpoint_alignment_rate(contrib_df: pd.DataFrame) -> float:
    if contrib_df.empty or "time_months" not in contrib_df.columns:
        return 0.0

    values = pd.to_numeric(contrib_df["time_months"], errors="coerce").dropna()
    if values.empty:
        return 0.0

    med = float(values.median())
    if med == 0:
        return 1.0

    aligned = (values.sub(med).abs() / med) <= 0.20
    return float(aligned.mean())


def _penalty_ecr_participants(value: float) -> int:
    if value < 0.70:
        return 30
    if value < 0.85:
        return 15
    return 5


def _penalty_reporting_debt(value: float) -> int:
    if value > 0.30:
        return 20
    if value > 0.15:
        return 10
    return 0


def _penalty_i2(i2: float) -> int:
    if i2 > 60:
        return 15
    if i2 > 40:
        return 8
    return 0


def _penalty_endpoint_mismatch(alignment_rate: float) -> int:
    mismatch = 1.0 - alignment_rate
    if mismatch > 0.25:
        return 10
    if mismatch > 0.10:
        return 5
    return 0


def _penalty_sparse(k: int) -> int:
    return 10 if k < 3 else 0


def build_trust_capsules(
    universe_df: pd.DataFrame,
    hfhosp_comp_df: pd.DataFrame,
    sae_comp_df: pd.DataFrame,
    hfhosp_summary: pd.DataFrame,
    sae_summary: pd.DataFrame,
    grace_months: int,
) -> pd.DataFrame:
    classes = sorted(
        set(universe_df["primary_intervention_class"].dropna().unique())
        | set(hfhosp_summary.get("intervention_class", []))
        | set(sae_summary.get("intervention_class", []))
    )

    summaries: Dict[str, Dict[str, pd.Series]] = {
        "HF_HOSPITALIZATION": {
            row["intervention_class"]: row
            for _, row in hfhosp_summary.iterrows()
        }
        if not hfhosp_summary.empty
        else {},
        "SAE": {
            row["intervention_class"]: row
            for _, row in sae_summary.iterrows()
        }
        if not sae_summary.empty
        else {},
    }

    comp_lookup = {
        "HF_HOSPITALIZATION": hfhosp_comp_df,
        "SAE": sae_comp_df,
    }

    rows: List[Dict[str, object]] = []
    for cls in classes:
        class_completed = _class_completed_universe(universe_df, cls)
        eligible_trials = len(class_completed)
        eligible_participants = _participant_sum(class_completed)
        debt_rate = _reporting_debt_rate(class_completed, grace_months)

        for outcome in ("HF_HOSPITALIZATION", "SAE"):
            comp_df = comp_lookup[outcome]
            comp_cls = comp_df[comp_df["intervention_class"] == cls] if not comp_df.empty else pd.DataFrame()

            contributing_trials = int(comp_cls["nct_id"].nunique()) if not comp_cls.empty else 0
            contributing_participants = float(comp_cls["n_t"].sum() + comp_cls["n_c"].sum()) if not comp_cls.empty else 0.0

            ecr_trials = (contributing_trials / eligible_trials) if eligible_trials else 0.0
            ecr_participants = (contributing_participants / eligible_participants) if eligible_participants else 0.0

            alignment_rate = _endpoint_alignment_rate(comp_cls)

            summary_row = summaries[outcome].get(cls)
            i2 = float(summary_row["i2"]) if summary_row is not None else np.nan
            k = int(summary_row["k_studies"]) if summary_row is not None else 0

            p_ecr = _penalty_ecr_participants(ecr_participants) if eligible_trials else 30
            p_debt = _penalty_reporting_debt(debt_rate)
            p_i2 = _penalty_i2(i2) if not np.isnan(i2) else 15
            p_mismatch = _penalty_endpoint_mismatch(alignment_rate)
            p_sparse = _penalty_sparse(k)
            trust_score = max(0, 100 - (p_ecr + p_debt + p_i2 + p_mismatch + p_sparse))

            rows.append(
                {
                    "intervention_class": cls,
                    "outcome": outcome,
                    "eligible_completed_trials": eligible_trials,
                    "eligible_completed_participants": eligible_participants,
                    "contributing_trials": contributing_trials,
                    "contributing_participants": contributing_participants,
                    "ecr_trials": ecr_trials,
                    "ecr_participants": ecr_participants,
                    "reporting_debt_rate": debt_rate,
                    "endpoint_alignment_rate": alignment_rate,
                    "heterogeneity_i2": i2,
                    "k_studies": k,
                    "penalty_ecr_participants": p_ecr,
                    "penalty_reporting_debt": p_debt,
                    "penalty_heterogeneity": p_i2,
                    "penalty_endpoint_mismatch": p_mismatch,
                    "penalty_sparse": p_sparse,
                    "trust_score": trust_score,
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["outcome", "intervention_class"]).reset_index(drop=True)
    return out
