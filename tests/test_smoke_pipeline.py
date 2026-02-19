import json
from pathlib import Path

import pandas as pd

from hfpef_registry_synth.config import PipelineConfig
from hfpef_registry_synth.pipeline import run_pipeline


def test_smoke_pipeline_with_fixture(tmp_path):
    fixture_path = Path(__file__).parent / "fixtures" / "mock_studies.json"
    studies = json.loads(fixture_path.read_text(encoding="utf-8"))["studies"]

    config = PipelineConfig(
        out_dir=tmp_path / "outputs",
        cache_dir=tmp_path / "cache",
        start_year=2015,
        grace_months=24,
        baseline_risks=[50, 100, 200],
        mnar_deltas=[0.0, 0.10, 0.20],
    )

    artifacts = run_pipeline(config=config, preloaded_studies=studies)

    assert not artifacts.universe_df.empty
    assert (config.out_dir / "trial_universe.csv").exists()
    assert (config.out_dir / "results_extract_hfhosp.csv").exists()
    assert (config.out_dir / "results_extract_sae.csv").exists()
    assert (config.out_dir / "synthesis_decision_table.csv").exists()
    assert (config.out_dir / "trust_capsules.csv").exists()
    assert (config.out_dir / "mnar_envelopes.csv").exists()
    assert (config.out_dir / "evidence_graph_edges.csv").exists()
    assert (config.out_dir / "summary_report.md").exists()

    trust_df = pd.read_csv(config.out_dir / "trust_capsules.csv")
    assert "trust_score" in trust_df.columns
