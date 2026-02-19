import pandas as pd

from hfpef_registry_synth.framework_alignment import build_framework_alignment_table


def test_framework_alignment_contains_mnar_mapping():
    trust_df = pd.DataFrame(
        [
            {
                "intervention_class": "SGLT2 inhibitors",
                "outcome": "HF_HOSPITALIZATION",
                "eligible_completed_trials": 3,
                "ecr_trials": 0.67,
                "ecr_participants": 0.71,
                "reporting_debt_rate": 0.22,
                "endpoint_alignment_rate": 1.0,
                "heterogeneity_i2": 10.0,
            }
        ]
    )
    mnar_df = pd.DataFrame(
        [
            {
                "intervention_class": "SGLT2 inhibitors",
                "outcome": "HF_HOSPITALIZATION",
                "delta": 0.10,
                "robust_under_scenario": True,
            },
            {
                "intervention_class": "SGLT2 inhibitors",
                "outcome": "HF_HOSPITALIZATION",
                "delta": 0.20,
                "robust_under_scenario": False,
            },
        ]
    )

    out = build_framework_alignment_table(trust_df, mnar_df)
    assert not out.empty
    assert "ROB-ME" in set(out["framework"])
    assert "mnar_robust_under_scenario" in set(out["metric"])
