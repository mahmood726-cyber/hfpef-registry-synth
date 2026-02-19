"""Model robustness checks for class-level synthesis."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import optimize


@dataclass
class MetaEstimate:
    method: str
    mu: float
    se: float
    ci_low: float
    ci_high: float
    tau2: float
    q: float
    k: int


def _clean_inputs(y: Sequence[float], v: Sequence[float]) -> Tuple[np.ndarray, np.ndarray]:
    y_arr = np.asarray(y, dtype=float)
    v_arr = np.asarray(v, dtype=float)
    mask = np.isfinite(y_arr) & np.isfinite(v_arr) & (v_arr > 0)
    return y_arr[mask], v_arr[mask]


def _compute_q(y: np.ndarray, v: np.ndarray, tau2: float) -> float:
    w = 1.0 / np.maximum(v + tau2, 1e-12)
    mu = float(np.sum(w * y) / np.sum(w))
    return float(np.sum(w * (y - mu) ** 2))


def _tau2_dl(y: np.ndarray, v: np.ndarray) -> Tuple[float, float]:
    if y.size <= 1:
        return 0.0, 0.0
    w = 1.0 / v
    mu = float(np.sum(w * y) / np.sum(w))
    q = float(np.sum(w * (y - mu) ** 2))
    df = y.size - 1
    c = float(np.sum(w) - np.sum(w**2) / np.sum(w))
    tau2 = max(0.0, (q - df) / c) if c > 0 else 0.0
    return tau2, q


def _tau2_pm(y: np.ndarray, v: np.ndarray) -> Tuple[float, float]:
    if y.size <= 1:
        return 0.0, 0.0
    df = y.size - 1
    q0 = _compute_q(y, v, 0.0)
    if q0 <= df:
        return 0.0, q0

    def objective(tau2: float) -> float:
        return _compute_q(y, v, tau2) - df

    hi = 1.0
    while objective(hi) > 0 and hi < 1e6:
        hi *= 2.0

    if hi >= 1e6 and objective(hi) > 0:
        tau2 = hi
    else:
        tau2 = float(optimize.brentq(objective, 0.0, hi, maxiter=200))
    return tau2, _compute_q(y, v, tau2)


def estimate_meta(y: Sequence[float], v: Sequence[float], method: str) -> Optional[MetaEstimate]:
    y_arr, v_arr = _clean_inputs(y, v)
    k = int(y_arr.size)
    if k == 0:
        return None

    m = method.strip().upper()
    if m not in {"FE", "DL", "PM"}:
        raise ValueError(f"Unsupported method: {method}")

    if m == "FE":
        tau2 = 0.0
        q = _compute_q(y_arr, v_arr, tau2) if k > 1 else 0.0
    elif m == "DL":
        tau2, q = _tau2_dl(y_arr, v_arr)
    else:
        tau2, q = _tau2_pm(y_arr, v_arr)

    w = 1.0 / np.maximum(v_arr + tau2, 1e-12)
    mu = float(np.sum(w * y_arr) / np.sum(w))
    se = math.sqrt(float(1.0 / np.sum(w)))
    ci_low = mu - 1.96 * se
    ci_high = mu + 1.96 * se

    return MetaEstimate(
        method=m,
        mu=mu,
        se=se,
        ci_low=ci_low,
        ci_high=ci_high,
        tau2=float(tau2),
        q=float(q),
        k=k,
    )


def _effect_direction(rr: float, ci_low_rr: float, ci_high_rr: float) -> str:
    if ci_high_rr < 1.0:
        return "benefit"
    if ci_low_rr > 1.0:
        return "harm"
    return "uncertain"


def run_model_robustness(comparisons_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return method-sensitivity and leave-one-out robustness tables."""
    if comparisons_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    model_rows: List[Dict[str, object]] = []
    loo_rows: List[Dict[str, object]] = []

    grouped = comparisons_df.groupby(["outcome", "intervention_class"], dropna=False)
    for (outcome, intervention_class), group in grouped:
        y = group["log_rr"].astype(float).tolist()
        v = group["var_log_rr"].astype(float).tolist()

        method_estimates: Dict[str, MetaEstimate] = {}
        for method in ("FE", "DL", "PM"):
            est = estimate_meta(y, v, method)
            if est is None:
                continue
            method_estimates[method] = est
            rr = math.exp(est.mu)
            ci_low_rr = math.exp(est.ci_low)
            ci_high_rr = math.exp(est.ci_high)
            model_rows.append(
                {
                    "outcome": outcome,
                    "intervention_class": intervention_class,
                    "method": method,
                    "k_studies": est.k,
                    "pooled_log_rr": est.mu,
                    "pooled_rr": rr,
                    "ci_low_rr": ci_low_rr,
                    "ci_high_rr": ci_high_rr,
                    "tau2": est.tau2,
                    "q": est.q,
                    "direction": _effect_direction(rr, ci_low_rr, ci_high_rr),
                }
            )

        if not method_estimates:
            continue

        directions = {
            _effect_direction(math.exp(m.mu), math.exp(m.ci_low), math.exp(m.ci_high))
            for m in method_estimates.values()
        }
        direction_concordant = len(directions) == 1

        y_arr, v_arr = _clean_inputs(y, v)
        loo_rr_values: List[float] = []
        if y_arr.size >= 3:
            for idx in range(y_arr.size):
                mask = np.ones(y_arr.size, dtype=bool)
                mask[idx] = False
                est = estimate_meta(y_arr[mask], v_arr[mask], "DL")
                if est is None:
                    continue
                loo_rr_values.append(math.exp(est.mu))

        loo_min = float(min(loo_rr_values)) if loo_rr_values else np.nan
        loo_max = float(max(loo_rr_values)) if loo_rr_values else np.nan
        loo_crosses_null = bool(loo_min <= 1.0 <= loo_max) if loo_rr_values else False
        dl_rr = math.exp(method_estimates.get("DL", next(iter(method_estimates.values()))).mu)
        pm_rr = math.exp(method_estimates.get("PM", next(iter(method_estimates.values()))).mu)
        fe_rr = math.exp(method_estimates.get("FE", next(iter(method_estimates.values()))).mu)
        max_abs_shift = float(max(abs(dl_rr - fe_rr), abs(dl_rr - pm_rr)))

        loo_rows.append(
            {
                "outcome": outcome,
                "intervention_class": intervention_class,
                "k_studies": int(y_arr.size),
                "direction_concordant_across_methods": direction_concordant,
                "dl_rr": dl_rr,
                "pm_rr": pm_rr,
                "fe_rr": fe_rr,
                "max_abs_rr_shift_vs_dl": max_abs_shift,
                "loo_runs": len(loo_rr_values),
                "loo_rr_min": loo_min,
                "loo_rr_max": loo_max,
                "loo_crosses_null": loo_crosses_null,
                "robustness_flag": bool(direction_concordant and not loo_crosses_null),
            }
        )

    model_df = pd.DataFrame(model_rows)
    loo_df = pd.DataFrame(loo_rows)

    if not model_df.empty:
        model_df = model_df.sort_values(["outcome", "intervention_class", "method"]).reset_index(drop=True)
    if not loo_df.empty:
        loo_df = loo_df.sort_values(["outcome", "intervention_class"]).reset_index(drop=True)

    return model_df, loo_df
