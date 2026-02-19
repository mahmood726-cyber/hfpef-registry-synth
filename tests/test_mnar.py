import math

import pandas as pd

from hfpef_registry_synth.mnar import build_mnar_envelopes


def test_mnar_falls_back_to_trial_fraction_when_enrollment_missing():
    universe_df = pd.DataFrame(
        [
            {
                "nct_id": "NCT_A",
                "primary_intervention_class": "SGLT2 inhibitors",
                "overall_status": "COMPLETED",
                "enrollment": None,
            },
            {
                "nct_id": "NCT_B",
                "primary_intervention_class": "SGLT2 inhibitors",
                "overall_status": "COMPLETED",
                "enrollment": None,
            },
        ]
    )
    comparisons_df = pd.DataFrame(
        [
            {
                "nct_id": "NCT_A",
                "intervention_class": "SGLT2 inhibitors",
                "outcome": "HF_HOSPITALIZATION",
            }
        ]
    )
    summary_df = pd.DataFrame(
        [
            {
                "intervention_class": "SGLT2 inhibitors",
                "pooled_log_rr": math.log(0.80),
            }
        ]
    )

    out = build_mnar_envelopes(
        universe_df=universe_df,
        comparisons_df=comparisons_df,
        summary_df=summary_df,
        outcome="HF_HOSPITALIZATION",
        deltas=[0.10],
        baseline_risk_per_1000=100,
        clinically_meaningful_arr=5.0,
    )

    assert len(out) == 1
    row = out.iloc[0]
    assert math.isclose(float(row["missing_fraction_participants"]), 0.0, rel_tol=1e-9)
    assert math.isclose(float(row["missing_fraction_trials"]), 0.5, rel_tol=1e-9)
    assert math.isclose(float(row["missing_fraction_used"]), 0.5, rel_tol=1e-9)
    assert row["missing_fraction_rule"] == "trial_fraction_no_enrollment"
