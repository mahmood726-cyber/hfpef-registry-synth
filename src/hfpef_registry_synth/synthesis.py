"""Class-based synthesis, meta-regression, and decision tables."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from .utils import normalize_ws


@dataclass
class MetaResult:
    mu: float
    se: float
    ci_low: float
    ci_high: float
    tau2: float
    i2: float
    q: float
    k: int


def compute_log_rr(
    e_t: float,
    n_t: float,
    e_c: float,
    n_c: float,
    continuity: float = 0.5,
) -> Tuple[Optional[float], Optional[float]]:
    if min(n_t, n_c) <= 0:
        return None, None
    if e_t < 0 or e_c < 0 or e_t > n_t or e_c > n_c:
        return None, None

    a = float(e_t)
    b = float(n_t - e_t)
    c = float(e_c)
    d = float(n_c - e_c)

    if min(a, b, c, d) == 0:
        a += continuity
        b += continuity
        c += continuity
        d += continuity

    n_t_adj = a + b
    n_c_adj = c + d
    if min(a, c, n_t_adj, n_c_adj) <= 0:
        return None, None

    rr = (a / n_t_adj) / (c / n_c_adj)
    if rr <= 0:
        return None, None

    log_rr = math.log(rr)
    var = (1.0 / a) - (1.0 / n_t_adj) + (1.0 / c) - (1.0 / n_c_adj)
    if var <= 0:
        return None, None
    return log_rr, var


def random_effects_meta(y: Sequence[float], v: Sequence[float]) -> Optional[MetaResult]:
    y_arr = np.asarray(y, dtype=float)
    v_arr = np.asarray(v, dtype=float)
    mask = np.isfinite(y_arr) & np.isfinite(v_arr) & (v_arr > 0)
    y_arr = y_arr[mask]
    v_arr = v_arr[mask]
    k = y_arr.size
    if k == 0:
        return None

    w_fe = 1.0 / v_arr
    mu_fe = float(np.sum(w_fe * y_arr) / np.sum(w_fe))

    if k == 1:
        se = math.sqrt(float(v_arr[0]))
        return MetaResult(
            mu=float(y_arr[0]),
            se=se,
            ci_low=float(y_arr[0] - 1.96 * se),
            ci_high=float(y_arr[0] + 1.96 * se),
            tau2=0.0,
            i2=0.0,
            q=0.0,
            k=1,
        )

    q = float(np.sum(w_fe * (y_arr - mu_fe) ** 2))
    df = k - 1
    c = float(np.sum(w_fe) - (np.sum(w_fe**2) / np.sum(w_fe)))
    tau2 = max(0.0, (q - df) / c) if c > 0 else 0.0

    w_re = 1.0 / (v_arr + tau2)
    mu_re = float(np.sum(w_re * y_arr) / np.sum(w_re))
    se_re = math.sqrt(float(1.0 / np.sum(w_re)))
    ci_low = mu_re - 1.96 * se_re
    ci_high = mu_re + 1.96 * se_re

    i2 = max(0.0, ((q - df) / q) * 100.0) if q > 0 else 0.0

    return MetaResult(
        mu=mu_re,
        se=se_re,
        ci_low=ci_low,
        ci_high=ci_high,
        tau2=tau2,
        i2=i2,
        q=q,
        k=k,
    )


def build_pairwise_comparisons(
    arm_df: pd.DataFrame,
    universe_df: pd.DataFrame,
    event_col: str,
    outcome_label: str,
    fallback_event_col: Optional[str] = None,
) -> pd.DataFrame:
    if arm_df.empty:
        return pd.DataFrame()

    trial_meta = universe_df.set_index("nct_id").to_dict(orient="index")
    rows: List[Dict[str, object]] = []

    for nct_id, g in arm_df.groupby("nct_id"):
        g = g.copy()

        if event_col not in g.columns:
            continue
        g["event"] = g[event_col]
        if fallback_event_col and fallback_event_col in g.columns:
            g.loc[g["event"].isna(), "event"] = g[fallback_event_col]

        g = g[g["event"].notna() & g["denominator"].notna()]
        if g.empty:
            continue

        g = g[g["denominator"].astype(float) > 0]
        if g.empty or len(g) < 2:
            continue

        comp = g[(g["arm_role"] == "comparator") | (g["arm_class"] == "Placebo/SoC")]
        if comp.empty:
            comp = g[g["arm_group_name"].str.contains("placebo|control|usual care|standard", case=False, na=False)]
        if comp.empty:
            continue

        comp_event = float(comp["event"].astype(float).sum())
        comp_n = float(comp["denominator"].astype(float).sum())
        if comp_n <= 0:
            continue

        trt = g.drop(index=comp.index)
        if trt.empty:
            continue

        class_groups: List[Tuple[str, pd.DataFrame]] = []
        for arm_class, g_class in trt.groupby("arm_class"):
            if normalize_ws(str(arm_class)).lower() in {"", "unknown", "placebo/soc"}:
                continue
            class_groups.append((arm_class, g_class))
        if not class_groups:
            continue

        # Shared controls in multi-arm trials are split across contrasts
        # to avoid unit-of-analysis bias from duplicated comparator data.
        split_factor = float(len(class_groups))
        comp_event_adj = comp_event / split_factor
        comp_n_adj = comp_n / split_factor

        for arm_class, g_class in class_groups:
            trt_event = float(g_class["event"].astype(float).sum())
            trt_n = float(g_class["denominator"].astype(float).sum())
            log_rr, var = compute_log_rr(trt_event, trt_n, comp_event_adj, comp_n_adj)
            if log_rr is None or var is None:
                continue

            meta = trial_meta.get(nct_id, {})
            arm_label = "; ".join(
                sorted({normalize_ws(str(x)) for x in g_class.get("arm_label", []) if normalize_ws(str(x))})
            )

            rows.append(
                {
                    "nct_id": nct_id,
                    "outcome": outcome_label,
                    "intervention_class": arm_class,
                    "intervention_label": arm_label,
                    "comparator_class": "Placebo/SoC",
                    "e_t": trt_event,
                    "n_t": trt_n,
                    "e_c": comp_event_adj,
                    "n_c": comp_n_adj,
                    "e_c_raw": comp_event,
                    "n_c_raw": comp_n,
                    "control_split_factor": split_factor,
                    "cer": comp_event / comp_n if comp_n else np.nan,
                    "log_rr": log_rr,
                    "var_log_rr": var,
                    "rr": math.exp(log_rr),
                    "ef_band": meta.get("ef_band", "unknown"),
                    "primary_completion_year": meta.get("primary_completion_year"),
                    "enrollment": meta.get("enrollment"),
                    "time_months": float(g_class["time_months"].dropna().max())
                    if "time_months" in g_class.columns and not g_class["time_months"].dropna().empty
                    else np.nan,
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["outcome", "intervention_class", "nct_id"]).reset_index(drop=True)
    return out


def _meta_regression(df_class: pd.DataFrame, tau2: float) -> pd.DataFrame:
    if len(df_class) < 3:
        return pd.DataFrame()

    y = df_class["log_rr"].astype(float).to_numpy()
    v = df_class["var_log_rr"].astype(float).to_numpy()
    cer = df_class["cer"].astype(float).to_numpy()

    ef_band = df_class["ef_band"].fillna("unknown").astype(str)
    ef_mixed = (ef_band == "mixed_or_midrange").astype(float).to_numpy()
    ef_unknown = (ef_band == "unknown").astype(float).to_numpy()

    year = pd.to_numeric(df_class["primary_completion_year"], errors="coerce").to_numpy()
    year_centered = year - np.nanmean(year)
    year_centered = np.where(np.isnan(year_centered), 0.0, year_centered)

    x = np.column_stack(
        [
            np.ones(len(df_class)),
            cer,
            ef_mixed,
            ef_unknown,
            year_centered,
        ]
    )

    w = 1.0 / np.maximum(v + tau2, 1e-12)
    xtw = x.T * w
    xtwx = xtw @ x
    xtwy = xtw @ y
    beta = np.linalg.pinv(xtwx) @ xtwy
    cov = np.linalg.pinv(xtwx)
    se = np.sqrt(np.clip(np.diag(cov), 0.0, None))

    terms = ["intercept", "cer", "ef_mixed", "ef_unknown", "year_centered"]
    return pd.DataFrame(
        {
            "term": terms,
            "beta": beta,
            "se": se,
            "ci_low": beta - 1.96 * se,
            "ci_high": beta + 1.96 * se,
        }
    )


def _partial_pool_by_drug(df_class: pd.DataFrame) -> Tuple[float, float, float, pd.DataFrame]:
    """Approximate class-based partial pooling over intervention labels within class."""
    grouped = []
    for label, g in df_class.groupby("intervention_label"):
        m = random_effects_meta(g["log_rr"].values, g["var_log_rr"].values)
        if m is None:
            continue
        grouped.append({"intervention_label": label or "unknown", "mu": m.mu, "var": m.se**2, "k": m.k})

    if not grouped:
        return np.nan, np.nan, 0.0, pd.DataFrame()

    drug_df = pd.DataFrame(grouped)
    if len(drug_df) == 1:
        mu = float(drug_df.iloc[0]["mu"])
        se = math.sqrt(float(drug_df.iloc[0]["var"]))
        return mu, se, 0.0, drug_df.assign(pooled_mu=mu, pooled_se=se, tau2_drug=0.0)

    theta = drug_df["mu"].to_numpy(dtype=float)
    var = np.maximum(drug_df["var"].to_numpy(dtype=float), 1e-12)
    w = 1.0 / var
    mu_fixed = float(np.sum(w * theta) / np.sum(w))

    q = float(np.sum(w * (theta - mu_fixed) ** 2))
    df = len(theta) - 1
    c = float(np.sum(w) - np.sum(w**2) / np.sum(w))
    tau2_drug = max(0.0, (q - df) / c) if c > 0 else 0.0

    if tau2_drug > 0:
        post_var = 1.0 / ((1.0 / var) + (1.0 / tau2_drug))
        post_mu = post_var * ((theta / var) + (mu_fixed / tau2_drug))
    else:
        post_var = var
        post_mu = theta

    w_post = 1.0 / np.maximum(post_var, 1e-12)
    class_mu = float(np.sum(w_post * post_mu) / np.sum(w_post))
    class_se = math.sqrt(float(1.0 / np.sum(w_post)))

    drug_df = drug_df.assign(
        pooled_mu=post_mu,
        pooled_se=np.sqrt(post_var),
        tau2_drug=tau2_drug,
    )
    return class_mu, class_se, tau2_drug, drug_df


def run_class_synthesis(comparisons_df: pd.DataFrame, outcome: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if comparisons_df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    dfo = comparisons_df[comparisons_df["outcome"] == outcome].copy()
    if dfo.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    summary_rows: List[Dict[str, object]] = []
    reg_rows: List[Dict[str, object]] = []
    shrink_rows: List[pd.DataFrame] = []

    for cls, g in dfo.groupby("intervention_class"):
        if len(g) == 0:
            continue

        re = random_effects_meta(g["log_rr"].values, g["var_log_rr"].values)
        if re is None:
            continue

        pooled_mu, pooled_se, tau2_drug, shrink_df = _partial_pool_by_drug(g)
        if math.isnan(pooled_mu) or math.isnan(pooled_se):
            pooled_mu = re.mu
            pooled_se = re.se
            tau2_drug = 0.0
            shrink_df = pd.DataFrame()

        ci_low = pooled_mu - 1.96 * pooled_se
        ci_high = pooled_mu + 1.96 * pooled_se

        summary_rows.append(
            {
                "outcome": outcome,
                "intervention_class": cls,
                "k_studies": int(re.k),
                "pooled_log_rr": pooled_mu,
                "pooled_rr": math.exp(pooled_mu),
                "ci_low_log_rr": ci_low,
                "ci_high_log_rr": ci_high,
                "ci_low_rr": math.exp(ci_low),
                "ci_high_rr": math.exp(ci_high),
                "tau2": float(re.tau2),
                "i2": float(re.i2),
                "q": float(re.q),
                "tau2_drug": float(tau2_drug),
                "n_participants_treated": int(g["n_t"].sum()),
                "n_participants_control": int(g["n_c"].sum()),
            }
        )

        reg_df = _meta_regression(g, re.tau2)
        if not reg_df.empty:
            reg_df = reg_df.assign(outcome=outcome, intervention_class=cls)
            reg_rows.append(reg_df)

        if not shrink_df.empty:
            shrink_df = shrink_df.assign(outcome=outcome, intervention_class=cls)
            shrink_rows.append(shrink_df)

    summary_df = pd.DataFrame(summary_rows)
    regression_df = pd.concat(reg_rows, ignore_index=True) if reg_rows else pd.DataFrame()
    shrinkage_df = pd.concat(shrink_rows, ignore_index=True) if shrink_rows else pd.DataFrame()

    if not summary_df.empty:
        summary_df = summary_df.sort_values("intervention_class").reset_index(drop=True)
    return summary_df, regression_df, shrinkage_df


def build_decision_table(
    hfhosp_summary: pd.DataFrame,
    sae_summary: pd.DataFrame,
    baseline_risks: Sequence[int],
) -> pd.DataFrame:
    baseline_risks = sorted({int(x) for x in baseline_risks if int(x) > 0})
    if not baseline_risks:
        baseline_risks = [50, 100, 200]

    hfhosp_lookup = hfhosp_summary.set_index("intervention_class").to_dict(orient="index") if not hfhosp_summary.empty else {}
    sae_lookup = sae_summary.set_index("intervention_class").to_dict(orient="index") if not sae_summary.empty else {}

    classes = sorted(set(hfhosp_lookup.keys()) | set(sae_lookup.keys()))
    rows: List[Dict[str, object]] = []

    for cls in classes:
        h = hfhosp_lookup.get(cls)
        s = sae_lookup.get(cls)
        for risk in baseline_risks:
            row: Dict[str, object] = {
                "intervention_class": cls,
                "baseline_risk_per_1000": risk,
            }

            if h:
                rr_h = float(h["pooled_rr"])
                rr_h_lo = float(h["ci_low_rr"])
                rr_h_hi = float(h["ci_high_rr"])
                arr = risk - (risk * rr_h)
                arr_lo = risk - (risk * rr_h_hi)
                arr_hi = risk - (risk * rr_h_lo)
                row.update(
                    {
                        "rr_hfhosp": rr_h,
                        "rr_hfhosp_ci_low": rr_h_lo,
                        "rr_hfhosp_ci_high": rr_h_hi,
                        "arr_hfhosp_per_1000": arr,
                        "arr_hfhosp_ci_low": arr_lo,
                        "arr_hfhosp_ci_high": arr_hi,
                    }
                )
            else:
                row.update(
                    {
                        "rr_hfhosp": np.nan,
                        "rr_hfhosp_ci_low": np.nan,
                        "rr_hfhosp_ci_high": np.nan,
                        "arr_hfhosp_per_1000": np.nan,
                        "arr_hfhosp_ci_low": np.nan,
                        "arr_hfhosp_ci_high": np.nan,
                    }
                )

            if s:
                rr_s = float(s["pooled_rr"])
                rr_s_lo = float(s["ci_low_rr"])
                rr_s_hi = float(s["ci_high_rr"])
                ari = (risk * rr_s) - risk
                ari_lo = (risk * rr_s_lo) - risk
                ari_hi = (risk * rr_s_hi) - risk
                row.update(
                    {
                        "rr_sae": rr_s,
                        "rr_sae_ci_low": rr_s_lo,
                        "rr_sae_ci_high": rr_s_hi,
                        "ari_sae_per_1000": ari,
                        "ari_sae_ci_low": ari_lo,
                        "ari_sae_ci_high": ari_hi,
                    }
                )
            else:
                row.update(
                    {
                        "rr_sae": np.nan,
                        "rr_sae_ci_low": np.nan,
                        "rr_sae_ci_high": np.nan,
                        "ari_sae_per_1000": np.nan,
                        "ari_sae_ci_low": np.nan,
                        "ari_sae_ci_high": np.nan,
                    }
                )

            arr = row.get("arr_hfhosp_per_1000")
            ari = row.get("ari_sae_per_1000")
            row["net_benefit_per_1000"] = (
                float(arr) - float(ari)
                if arr is not None and ari is not None and not (pd.isna(arr) or pd.isna(ari))
                else np.nan
            )
            rows.append(row)

    return pd.DataFrame(rows)
