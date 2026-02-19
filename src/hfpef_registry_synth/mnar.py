"""Transparency-adjusted MNAR sensitivity envelopes."""

from __future__ import annotations

import math
from typing import Dict, List, Sequence

import pandas as pd

from .utils import normalize_ws, parse_json_list


def _safe_fraction(num: float, den: float) -> float:
    if den <= 0:
        return 0.0
    frac = float(num) / float(den)
    return max(0.0, min(1.0, frac))


def _trial_mentions_class(row: pd.Series, cls: str) -> bool:
    target = normalize_ws(str(cls)).lower()
    primary = normalize_ws(str(row.get("primary_intervention_class", ""))).lower()
    if primary == target:
        return True
    for item in parse_json_list(row.get("intervention_classes")):
        if normalize_ws(str(item)).lower() == target:
            return True
    return False


def _completed_universe(universe_df: pd.DataFrame, cls: str) -> pd.DataFrame:
    if universe_df.empty:
        return universe_df
    status_mask = universe_df["overall_status"].fillna("").astype(str).str.upper() == "COMPLETED"
    class_mask = universe_df.apply(_trial_mentions_class, axis=1, cls=cls)
    return universe_df[status_mask & class_mask]


def build_mnar_envelopes(
    universe_df: pd.DataFrame,
    comparisons_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    outcome: str,
    deltas: Sequence[float],
    baseline_risk_per_1000: int,
    clinically_meaningful_arr: float,
) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame()

    rows: List[Dict[str, object]] = []

    for _, srow in summary_df.iterrows():
        cls = srow["intervention_class"]
        observed_mu = float(srow["pooled_log_rr"])
        observed_rr = float(math.exp(observed_mu))

        class_completed = _completed_universe(universe_df, cls)
        eligible_trials = int(class_completed["nct_id"].nunique())
        enroll_series = pd.to_numeric(class_completed["enrollment"], errors="coerce")
        enroll_pos = enroll_series[enroll_series > 0]
        total_participants = float(enroll_pos.sum())
        enrollment_coverage = _safe_fraction(float(enroll_pos.shape[0]), float(eligible_trials))

        comp_cls = comparisons_df[(comparisons_df["intervention_class"] == cls) & (comparisons_df["outcome"] == outcome)]
        observed_trials = int(comp_cls["nct_id"].nunique()) if not comp_cls.empty else 0
        observed_ncts = set(comp_cls["nct_id"].astype(str)) if not comp_cls.empty else set()

        missing_df = class_completed[~class_completed["nct_id"].isin(observed_ncts)]
        missing_trials = int(missing_df["nct_id"].nunique())
        missing_enroll = pd.to_numeric(missing_df["enrollment"], errors="coerce")
        missing_participants = float(missing_enroll[missing_enroll > 0].sum())

        m_participants = _safe_fraction(missing_participants, total_participants)
        m_trials = _safe_fraction(float(missing_trials), float(eligible_trials))

        if total_participants <= 0:
            m = m_trials
            m_rule = "trial_fraction_no_enrollment"
        elif enrollment_coverage < 0.70:
            m = max(m_participants, m_trials)
            m_rule = "max_participant_trial_fraction_low_enrollment_coverage"
        else:
            m = m_participants
            m_rule = "participant_fraction"

        obs_absolute = baseline_risk_per_1000 - (baseline_risk_per_1000 * observed_rr)

        for delta in deltas:
            scenario = f"delta_{delta:+.2f}" if delta != 0 else "S0_MAR"
            adjusted_mu = observed_mu + (m * float(delta))
            adjusted_rr = float(math.exp(adjusted_mu))
            adjusted_absolute = baseline_risk_per_1000 - (baseline_risk_per_1000 * adjusted_rr)

            conclusion_change = "stable"
            robust = True
            if outcome == "HF_HOSPITALIZATION":
                if observed_rr < 1.0 and adjusted_rr >= 1.0:
                    conclusion_change = "benefit_lost"
                    robust = False
                elif obs_absolute >= clinically_meaningful_arr and adjusted_absolute < clinically_meaningful_arr:
                    conclusion_change = "crosses_clinical_threshold"
                    robust = False
            else:  # SAE
                obs_harm = (baseline_risk_per_1000 * observed_rr) - baseline_risk_per_1000
                adj_harm = (baseline_risk_per_1000 * adjusted_rr) - baseline_risk_per_1000
                if obs_harm <= clinically_meaningful_arr and adj_harm > clinically_meaningful_arr:
                    conclusion_change = "harm_threshold_crossed"
                    robust = False

            rows.append(
                {
                    "outcome": outcome,
                    "intervention_class": cls,
                    "scenario": scenario,
                    "delta": float(delta),
                    "missing_fraction_participants": m_participants,
                    "missing_fraction_trials": m_trials,
                    "missing_fraction_used": m,
                    "missing_fraction_rule": m_rule,
                    "enrollment_coverage": enrollment_coverage,
                    "eligible_completed_trials": eligible_trials,
                    "observed_trials": observed_trials,
                    "missing_trials": missing_trials,
                    "total_participants": total_participants,
                    "missing_participants": missing_participants,
                    "observed_rr": observed_rr,
                    "adjusted_rr": adjusted_rr,
                    "observed_absolute_per_1000": obs_absolute,
                    "adjusted_absolute_per_1000": adjusted_absolute,
                    "conclusion_change": conclusion_change,
                    "robust_under_scenario": robust,
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["outcome", "intervention_class", "delta"]).reset_index(drop=True)
    return out
