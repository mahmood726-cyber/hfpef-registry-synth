import pandas as pd

from hfpef_registry_synth.credibility import run_external_credibility_checks


def test_external_credibility_detects_concordance_for_sglt2_hf():
    hfhosp_summary = pd.DataFrame(
        [
            {
                "intervention_class": "SGLT2 inhibitors",
                "pooled_rr": 0.80,
                "ci_low_rr": 0.70,
                "ci_high_rr": 0.92,
            }
        ]
    )
    sae_summary = pd.DataFrame()

    out = run_external_credibility_checks(hfhosp_summary, sae_summary)
    row = out[
        (out["intervention_class"] == "SGLT2 inhibitors")
        & (out["outcome"] == "HF_HOSPITALIZATION")
    ].iloc[0]

    assert row["observed_direction"] == "benefit"
    assert row["concordance"] == "full_concordance"
