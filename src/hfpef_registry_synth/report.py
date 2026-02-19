"""Markdown reporting helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from .config import PipelineConfig


def _top_lines(df: pd.DataFrame, cols: Iterable[str], n: int = 8) -> str:
    if df.empty:
        return "- None\n"
    lines = []
    subset = df[list(cols)].head(n)
    for _, row in subset.iterrows():
        kv = ", ".join(f"{c}={row[c]}" for c in subset.columns)
        lines.append(f"- {kv}")
    return "\n".join(lines) + "\n"


def write_summary_report(
    path: Path,
    config: PipelineConfig,
    universe_df: pd.DataFrame,
    hfhosp_summary: pd.DataFrame,
    sae_summary: pd.DataFrame,
    decision_df: pd.DataFrame,
    trust_df: pd.DataFrame,
    mnar_df: pd.DataFrame,
    robustness_models_df: pd.DataFrame,
    robustness_loo_df: pd.DataFrame,
    validation_metrics_df: pd.DataFrame,
    credibility_df: pd.DataFrame,
    framework_df: pd.DataFrame,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    completed = int((universe_df["overall_status"].str.upper() == "COMPLETED").sum()) if not universe_df.empty else 0
    posted = int(universe_df.get("results_posted", pd.Series(dtype=bool)).fillna(False).astype(bool).sum()) if not universe_df.empty else 0
    linked = int(universe_df.get("has_publication_link", pd.Series(dtype=bool)).fillna(False).astype(bool).sum()) if not universe_df.empty else 0

    text = f"""# HFpEF Registry-First Transparency-Adjusted Synthesis

Generated: {now}

## Registry-First Principle
This report treats trial registrations/protocols as the denominator truth layer and explicitly accounts for missing results as measurable reporting debt.

## Run Configuration
- start_year: {config.start_year}
- grace_months: {config.grace_months}
- baseline_risks_per_1000: {','.join(map(str, config.baseline_risks))}
- mnar_deltas: {','.join(map(str, config.mnar_deltas))}
- use_pubmed: {config.use_pubmed}
- use_openalex: {config.use_openalex}

## Trial Universe Snapshot
- Eligible HFpEF interventional trials: {len(universe_df)}
- Completed trials: {completed}
- Trials with posted CT.gov results module: {posted}
- Trials with publication linkage (PubMed/OpenAlex): {linked}

## HF Hospitalization Synthesis (Class-level)
{_top_lines(hfhosp_summary, ["intervention_class", "k_studies", "pooled_rr", "ci_low_rr", "ci_high_rr", "i2"]) }

## SAE Synthesis (Class-level)
{_top_lines(sae_summary, ["intervention_class", "k_studies", "pooled_rr", "ci_low_rr", "ci_high_rr", "i2"]) }

## Decision-Grade Absolute Effects (per 1000)
{_top_lines(decision_df, ["intervention_class", "baseline_risk_per_1000", "arr_hfhosp_per_1000", "ari_sae_per_1000", "net_benefit_per_1000"]) }

## Trust Capsules
{_top_lines(trust_df, ["intervention_class", "outcome", "ecr_trials", "ecr_participants", "reporting_debt_rate", "trust_score"]) }

## MNAR Transparency-Adjusted Sensitivity
{_top_lines(mnar_df, ["intervention_class", "outcome", "scenario", "observed_rr", "adjusted_rr", "conclusion_change", "robust_under_scenario"]) }

## Statistical Robustness (Model and Influence)
{_top_lines(robustness_models_df, ["intervention_class", "outcome", "method", "pooled_rr", "ci_low_rr", "ci_high_rr", "direction"]) }
{_top_lines(robustness_loo_df, ["intervention_class", "outcome", "direction_concordant_across_methods", "max_abs_rr_shift_vs_dl", "loo_crosses_null", "robustness_flag"]) }

## Manual Adjudication Validation
{_top_lines(validation_metrics_df, ["domain", "n_reviewed", "accuracy", "sensitivity", "specificity", "misclassification_rate", "status"]) }

## External Face-Validity Checks
{_top_lines(credibility_df, ["intervention_class", "outcome", "expected_direction", "observed_direction", "concordance"]) }

## Reporting-Bias Framework Alignment
{_top_lines(framework_df, ["intervention_class", "outcome", "metric", "value", "framework", "framework_item"]) }

## Interpretation Notes
- No SUCRA or ordinal ranking is produced.
- Decision support is expressed as absolute effects and net tradeoffs with uncertainty.
- Trust score is explicit and editable, not a black-box model.
- Robustness tables compare fixed-effect, DL random-effects, and Paule-Mandel random-effects estimates with leave-one-out stress tests.
- Validation metrics are scored against manually adjudicated consensus labels when provided; otherwise templates are generated for reviewer completion.
- Reporting-bias alignment table links each transparency metric to PRISMA/SW-iM/ROB-ME reporting domains.

## Known Limitations
- Registry outcomes may not align exactly with publication endpoint definitions.
- Missing PDFs and non-posted results remain partially unobserved by design.
- SAE synthesis uses participant-level totals where available (total SAE rows or event-group serious totals); event-count-only SAE tables are flagged and excluded from pooled RR.
"""

    path.write_text(text, encoding="utf-8")
