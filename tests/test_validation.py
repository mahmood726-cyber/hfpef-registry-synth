import math

import pandas as pd

from hfpef_registry_synth.validation import build_validation_outputs, compute_adjudication_metrics


def _mock_studies():
    return {
        "NCTVAL1": {
            "protocolSection": {
                "identificationModule": {
                    "nctId": "NCTVAL1",
                    "briefTitle": "Validation Trial 1",
                }
            },
            "resultsSection": {
                "outcomeMeasuresModule": {
                    "outcomeMeasures": [
                        {
                            "title": "Hospitalization for heart failure",
                            "description": "Participants with at least one hospitalization for heart failure",
                            "timeFrame": "12 months",
                        },
                        {
                            "title": "Composite of death or hospitalization",
                            "description": "Composite endpoint",
                            "timeFrame": "12 months",
                        },
                    ]
                }
            },
        }
    }


def test_build_validation_outputs_generates_candidates_and_sample():
    out = build_validation_outputs(
        studies=_mock_studies(),
        sample_size_per_domain=4,
        seed=123,
        adjudication_df=None,
    )
    assert not out.candidates_df.empty
    assert not out.sample_df.empty
    assert set(out.candidates_df["domain"]) == {"HF_HOSPITALIZATION", "SAE"}
    assert "status" in out.metrics_df.columns


def test_compute_adjudication_metrics_perfect_agreement():
    out = build_validation_outputs(
        studies=_mock_studies(),
        sample_size_per_domain=4,
        seed=123,
        adjudication_df=None,
    )
    candidates = out.candidates_df.copy()

    adjud = candidates[["domain", "nct_id", "outcome_idx", "algorithm_selected"]].copy()
    adjud["consensus_include"] = adjud["algorithm_selected"].astype(int)

    metrics_df, mis_df = compute_adjudication_metrics(adjud, candidates)
    assert not metrics_df.empty
    assert mis_df.empty
    for acc in metrics_df["accuracy"].tolist():
        assert math.isclose(float(acc), 1.0, rel_tol=1e-9)
