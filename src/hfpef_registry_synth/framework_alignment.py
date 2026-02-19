"""Map trust/transparency metrics to reporting-bias guidance frameworks."""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd


FRAMEWORK_MAP = {
    "eligible_completed_trials": {
        "framework": "PRISMA 2020",
        "item": "Item 16a (study selection)",
        "guidance": "Report denominator of studies assessed/eligible and included.",
    },
    "ecr_trials": {
        "framework": "SWiM",
        "item": "Item 5/6 (synthesis grouping and data contribution)",
        "guidance": "State how many eligible studies contribute to each synthesis.",
    },
    "ecr_participants": {
        "framework": "SWiM",
        "item": "Item 5/6 (synthesis grouping and data contribution)",
        "guidance": "Describe participant-weighted contribution and missingness.",
    },
    "reporting_debt_rate": {
        "framework": "ROB-ME",
        "item": "Risk due to missing results",
        "guidance": "Assess proportion of completed but unreported studies for each synthesis.",
    },
    "endpoint_alignment_rate": {
        "framework": "SWiM",
        "item": "Item 7 (standardised metric and comparability)",
        "guidance": "Document endpoint/timeframe alignment across included studies.",
    },
    "heterogeneity_i2": {
        "framework": "PRISMA 2020",
        "item": "Item 20b/20d (results of syntheses, heterogeneity)",
        "guidance": "Report heterogeneity and uncertainty for synthesis estimates.",
    },
    "mnar_robust_under_scenario": {
        "framework": "ROB-ME",
        "item": "Sensitivity analysis under plausible missing evidence",
        "guidance": "Evaluate whether conclusions remain stable under non-random missingness assumptions.",
    },
}


def _framework_row(
    intervention_class: str,
    outcome: str,
    metric: str,
    value: Any,
) -> Dict[str, Any]:
    meta = FRAMEWORK_MAP[metric]
    return {
        "intervention_class": intervention_class,
        "outcome": outcome,
        "metric": metric,
        "value": value,
        "framework": meta["framework"],
        "framework_item": meta["item"],
        "guidance_interpretation": meta["guidance"],
    }


def build_framework_alignment_table(trust_df: pd.DataFrame, mnar_df: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    if not trust_df.empty:
        metrics = [
            "eligible_completed_trials",
            "ecr_trials",
            "ecr_participants",
            "reporting_debt_rate",
            "endpoint_alignment_rate",
            "heterogeneity_i2",
        ]
        for _, row in trust_df.iterrows():
            for metric in metrics:
                rows.append(
                    _framework_row(
                        intervention_class=str(row.get("intervention_class", "")),
                        outcome=str(row.get("outcome", "")),
                        metric=metric,
                        value=row.get(metric, np.nan),
                    )
                )

    if not mnar_df.empty:
        # Worst-case (largest delta) scenario used as the ROB-ME sensitivity anchor.
        mnar = mnar_df.copy()
        mnar["delta"] = pd.to_numeric(mnar["delta"], errors="coerce")
        mnar = mnar[mnar["delta"].notna()]
        if not mnar.empty:
            idx = mnar.groupby(["intervention_class", "outcome"])["delta"].idxmax()
            worst = mnar.loc[idx]
            for _, row in worst.iterrows():
                rows.append(
                    _framework_row(
                        intervention_class=str(row.get("intervention_class", "")),
                        outcome=str(row.get("outcome", "")),
                        metric="mnar_robust_under_scenario",
                        value=bool(row.get("robust_under_scenario", False)),
                    )
                )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["outcome", "intervention_class", "metric"]).reset_index(drop=True)
    return out
