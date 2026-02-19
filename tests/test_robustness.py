import pandas as pd

from hfpef_registry_synth.robustness import run_model_robustness


def test_run_model_robustness_outputs_methods_and_loo():
    comparisons_df = pd.DataFrame(
        [
            {
                "outcome": "HF_HOSPITALIZATION",
                "intervention_class": "SGLT2 inhibitors",
                "log_rr": -0.20,
                "var_log_rr": 0.05,
            },
            {
                "outcome": "HF_HOSPITALIZATION",
                "intervention_class": "SGLT2 inhibitors",
                "log_rr": -0.10,
                "var_log_rr": 0.04,
            },
            {
                "outcome": "HF_HOSPITALIZATION",
                "intervention_class": "SGLT2 inhibitors",
                "log_rr": -0.30,
                "var_log_rr": 0.06,
            },
        ]
    )

    model_df, loo_df = run_model_robustness(comparisons_df)

    assert set(model_df["method"]) == {"FE", "DL", "PM"}
    row = loo_df.iloc[0]
    assert int(row["k_studies"]) == 3
    assert int(row["loo_runs"]) == 3
