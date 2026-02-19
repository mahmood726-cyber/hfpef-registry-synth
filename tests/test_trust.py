import math

import pandas as pd

from hfpef_registry_synth.trust import build_trust_capsules


def test_trust_denominator_uses_intervention_classes_membership():
    universe_df = pd.DataFrame(
        [
            {
                "nct_id": "NCT_A",
                "primary_intervention_class": "Other",
                "intervention_classes": '["sGC stimulators"]',
                "overall_status": "COMPLETED",
                "enrollment": 100,
                "primary_completion_date": "2020-01-01",
                "results_posted": False,
                "has_publication_link": False,
            },
            {
                "nct_id": "NCT_B",
                "primary_intervention_class": "sGC stimulators",
                "intervention_classes": '["sGC stimulators"]',
                "overall_status": "COMPLETED",
                "enrollment": 120,
                "primary_completion_date": "2020-01-01",
                "results_posted": True,
                "has_publication_link": False,
            },
        ]
    )
    hfhosp_comp_df = pd.DataFrame(
        [
            {
                "nct_id": "NCT_B",
                "intervention_class": "sGC stimulators",
                "n_t": 91,
                "n_c": 90,
                "time_months": 12.0,
            }
        ]
    )
    sae_comp_df = hfhosp_comp_df.copy()
    hfhosp_summary = pd.DataFrame(
        [{"intervention_class": "sGC stimulators", "i2": 0.0, "k_studies": 1}]
    )
    sae_summary = pd.DataFrame(
        [{"intervention_class": "sGC stimulators", "i2": 0.0, "k_studies": 1}]
    )

    out = build_trust_capsules(
        universe_df=universe_df,
        hfhosp_comp_df=hfhosp_comp_df,
        sae_comp_df=sae_comp_df,
        hfhosp_summary=hfhosp_summary,
        sae_summary=sae_summary,
        grace_months=24,
    )

    row = out[(out["intervention_class"] == "sGC stimulators") & (out["outcome"] == "HF_HOSPITALIZATION")].iloc[0]
    assert int(row["eligible_completed_trials"]) == 2
    assert int(row["contributing_trials"]) == 1
    assert math.isclose(float(row["ecr_trials"]), 0.5, rel_tol=1e-9)
