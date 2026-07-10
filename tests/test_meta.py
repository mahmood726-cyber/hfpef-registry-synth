import math

import pandas as pd

from hfpef_registry_synth.robustness import estimate_meta
from hfpef_registry_synth.synthesis import (
    _is_noncontrast_arm_group,
    _partial_pool_by_drug,
    build_pairwise_comparisons,
    compute_log_rr,
    random_effects_meta,
)


def test_random_effects_meta_empty_returns_none():
    assert random_effects_meta([], []) is None


def test_random_effects_meta_single_study_uses_v_directly():
    res = random_effects_meta([-0.3], [0.04])
    assert res is not None
    assert res.k == 1
    assert math.isclose(res.mu, -0.3, rel_tol=1e-9)
    assert math.isclose(res.se, 0.2, rel_tol=1e-9)  # sqrt(0.04)
    assert res.tau2 == 0.0
    assert res.i2 == 0.0
    assert res.q == 0.0
    assert math.isclose(res.ci_low, -0.3 - 1.96 * 0.2, rel_tol=1e-9)
    assert math.isclose(res.ci_high, -0.3 + 1.96 * 0.2, rel_tol=1e-9)


def test_random_effects_meta_drops_nonpositive_variance():
    # Only the finite, positive-variance study survives the mask -> k=1 branch.
    res = random_effects_meta([-0.3, -0.2], [0.04, 0.0])
    assert res is not None
    assert res.k == 1
    assert math.isclose(res.mu, -0.3, rel_tol=1e-9)


def test_estimate_meta_empty_returns_none():
    assert estimate_meta([], [], "DL") is None


def test_estimate_meta_all_invalid_variance_returns_none():
    assert estimate_meta([-0.3, -0.2], [0.0, -1.0], "DL") is None


def test_estimate_meta_single_study_all_methods():
    for method in ("FE", "DL", "PM"):
        est = estimate_meta([-0.3], [0.04], method)
        assert est is not None, method
        assert est.method == method
        assert est.k == 1
        assert math.isclose(est.mu, -0.3, rel_tol=1e-9), method
        assert math.isclose(est.se, 0.2, rel_tol=1e-9), method  # sqrt(0.04)
        assert est.tau2 == 0.0, method
        assert est.q == 0.0, method
        assert math.isclose(est.ci_low, -0.3 - 1.96 * 0.2, rel_tol=1e-9), method
        assert math.isclose(est.ci_high, -0.3 + 1.96 * 0.2, rel_tol=1e-9), method


def test_estimate_meta_rejects_unknown_method():
    try:
        estimate_meta([-0.3, -0.2], [0.04, 0.03], "REML")
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_compute_log_rr_basic():
    log_rr, var = compute_log_rr(e_t=20, n_t=100, e_c=40, n_c=100)
    assert log_rr is not None
    assert var is not None
    assert math.isclose(log_rr, math.log(0.5), rel_tol=1e-6)
    assert var > 0


def test_random_effects_meta_runs():
    y = [-0.3, -0.2, -0.1]
    v = [0.04, 0.03, 0.05]
    res = random_effects_meta(y, v)
    assert res is not None
    assert res.k == 3
    assert res.se > 0
    assert res.ci_low < res.mu < res.ci_high


def test_partial_pool_by_drug_single_label_returns_source_estimate():
    df = pd.DataFrame(
        [
            {
                "intervention_label": "empagliflozin",
                "log_rr": -0.30,
                "var_log_rr": 0.04,
            }
        ]
    )

    mu, se, tau2_drug, shrink_df = _partial_pool_by_drug(df)

    assert math.isclose(mu, -0.30, rel_tol=1e-9)
    assert math.isclose(se, 0.20, rel_tol=1e-9)
    assert tau2_drug == 0.0
    assert shrink_df.to_dict("records")[0]["intervention_label"] == "empagliflozin"


def test_build_pairwise_comparisons_splits_shared_control_for_multiarm_trial():
    arm_df = pd.DataFrame(
        [
            {
                "nct_id": "NCT_MULTI_1",
                "arm_role": "treatment",
                "arm_class": "SGLT2 inhibitors",
                "arm_group_name": "Empagliflozin",
                "arm_label": "empagliflozin",
                "events": 20,
                "denominator": 100,
                "time_months": 12,
            },
            {
                "nct_id": "NCT_MULTI_1",
                "arm_role": "treatment",
                "arm_class": "MRA",
                "arm_group_name": "Spironolactone",
                "arm_label": "spironolactone",
                "events": 25,
                "denominator": 100,
                "time_months": 12,
            },
            {
                "nct_id": "NCT_MULTI_1",
                "arm_role": "comparator",
                "arm_class": "Placebo/SoC",
                "arm_group_name": "Placebo",
                "arm_label": "placebo",
                "events": 30,
                "denominator": 100,
                "time_months": 12,
            },
        ]
    )
    universe_df = pd.DataFrame(
        [
            {
                "nct_id": "NCT_MULTI_1",
                "ef_band": "strict_hfpef",
                "primary_completion_year": 2021,
                "enrollment": 300,
            }
        ]
    )

    out = build_pairwise_comparisons(
        arm_df=arm_df,
        universe_df=universe_df,
        event_col="events",
        outcome_label="HF_HOSPITALIZATION",
    )

    assert len(out) == 2
    assert set(out["intervention_class"]) == {"SGLT2 inhibitors", "MRA"}
    assert set(out["control_split_factor"]) == {2.0}
    assert set(out["e_c_raw"]) == {30.0}
    assert set(out["n_c_raw"]) == {100.0}
    assert set(out["e_c"]) == {15.0}
    assert set(out["n_c"]) == {50.0}
    assert math.isclose(float(out["e_c"].sum()), 30.0, rel_tol=1e-9)
    assert math.isclose(float(out["n_c"].sum()), 100.0, rel_tol=1e-9)


def test_build_pairwise_comparisons_without_fallback_ignores_event_count_only_sae_rows():
    arm_df = pd.DataFrame(
        [
            {
                "nct_id": "NCT_SAE_EVENTS_ONLY",
                "arm_role": "treatment",
                "arm_class": "SGLT2 inhibitors",
                "arm_group_name": "Empagliflozin",
                "arm_label": "empagliflozin",
                "subjects_with_sae": None,
                "event_count": 20,
                "denominator": 100,
                "time_months": 12,
            },
            {
                "nct_id": "NCT_SAE_EVENTS_ONLY",
                "arm_role": "comparator",
                "arm_class": "Placebo/SoC",
                "arm_group_name": "Placebo",
                "arm_label": "placebo",
                "subjects_with_sae": None,
                "event_count": 18,
                "denominator": 100,
                "time_months": 12,
            },
        ]
    )
    universe_df = pd.DataFrame(
        [
            {
                "nct_id": "NCT_SAE_EVENTS_ONLY",
                "ef_band": "strict_hfpef",
                "primary_completion_year": 2021,
                "enrollment": 200,
            }
        ]
    )

    out = build_pairwise_comparisons(
        arm_df=arm_df,
        universe_df=universe_df,
        event_col="subjects_with_sae",
        outcome_label="SAE",
    )

    assert out.empty


def test_noncontrast_arm_group_detection():
    assert _is_noncontrast_arm_group("All Patients")
    assert _is_noncontrast_arm_group("Single Arm")
    assert _is_noncontrast_arm_group("Pooled Cohort")
    assert not _is_noncontrast_arm_group("Placebo")
    assert not _is_noncontrast_arm_group("Empagliflozin 10 mg")


def test_build_pairwise_comparisons_excludes_noncontrast_group_rows():
    arm_df = pd.DataFrame(
        [
            {
                "nct_id": "NCT_NONCONTRAST",
                "arm_role": "treatment",
                "arm_class": "Other",
                "arm_group_name": "All Patients",
                "arm_label": "all patients",
                "events": 100,
                "denominator": 500,
                "time_months": 12,
            },
            {
                "nct_id": "NCT_NONCONTRAST",
                "arm_role": "treatment",
                "arm_class": "SGLT2 inhibitors",
                "arm_group_name": "Empagliflozin",
                "arm_label": "empagliflozin",
                "events": 20,
                "denominator": 100,
                "time_months": 12,
            },
            {
                "nct_id": "NCT_NONCONTRAST",
                "arm_role": "comparator",
                "arm_class": "Placebo/SoC",
                "arm_group_name": "Placebo",
                "arm_label": "placebo",
                "events": 30,
                "denominator": 100,
                "time_months": 12,
            },
        ]
    )
    universe_df = pd.DataFrame(
        [
            {
                "nct_id": "NCT_NONCONTRAST",
                "ef_band": "strict_hfpef",
                "primary_completion_year": 2021,
                "enrollment": 700,
            }
        ]
    )

    out = build_pairwise_comparisons(
        arm_df=arm_df,
        universe_df=universe_df,
        event_col="events",
        outcome_label="HF_HOSPITALIZATION",
    )

    assert len(out) == 1
    row = out.iloc[0]
    assert row["intervention_class"] == "SGLT2 inhibitors"
    assert math.isclose(float(row["e_t"]), 20.0, rel_tol=1e-9)
    assert math.isclose(float(row["n_t"]), 100.0, rel_tol=1e-9)


def test_comparator_fallback_does_not_match_standardized_label_as_standard_of_care():
    arm_df = pd.DataFrame(
        [
            {
                "nct_id": "NCT_STD_LABEL",
                "arm_role": "treatment",
                "arm_class": "Other",
                "arm_group_name": "Standardized Exercise Program",
                "arm_label": "standardized exercise",
                "events": 12,
                "denominator": 100,
                "time_months": 12,
            },
            {
                "nct_id": "NCT_STD_LABEL",
                "arm_role": "treatment",
                "arm_class": "Other",
                "arm_group_name": "Personalized Exercise Program",
                "arm_label": "personalized exercise",
                "events": 10,
                "denominator": 100,
                "time_months": 12,
            },
        ]
    )
    universe_df = pd.DataFrame(
        [
            {
                "nct_id": "NCT_STD_LABEL",
                "ef_band": "strict_hfpef",
                "primary_completion_year": 2021,
                "enrollment": 200,
            }
        ]
    )

    out = build_pairwise_comparisons(
        arm_df=arm_df,
        universe_df=universe_df,
        event_col="events",
        outcome_label="HF_HOSPITALIZATION",
    )

    assert out.empty
