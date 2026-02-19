"""CLI: export evidence graph from existing outputs CSV files."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hfpef_registry_synth.graph_export import build_evidence_graph
from hfpef_registry_synth.logging_utils import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Export HFpEF evidence graph")
    parser.add_argument("--out_dir", default="outputs", help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    logger = setup_logging(name="hfpef_registry_synth.export_graph")

    universe_path = out_dir / "trial_universe.csv"
    hfhosp_path = out_dir / "results_extract_hfhosp.csv"
    sae_path = out_dir / "results_extract_sae.csv"

    if not universe_path.exists():
        raise FileNotFoundError(f"Missing required file: {universe_path}")

    universe_df = pd.read_csv(universe_path)
    hfhosp_df = pd.read_csv(hfhosp_path) if hfhosp_path.exists() else pd.DataFrame()
    sae_df = pd.read_csv(sae_path) if sae_path.exists() else pd.DataFrame()

    graph = build_evidence_graph(universe_df, hfhosp_df, sae_df)
    graph.edges.to_csv(out_dir / "evidence_graph_edges.csv", index=False)
    graph.trial_nodes.to_csv(out_dir / "evidence_graph_nodes_trials.csv", index=False)
    graph.class_nodes.to_csv(out_dir / "evidence_graph_nodes_intervention_classes.csv", index=False)

    logger.info("Graph export complete: %d edges", len(graph.edges))


if __name__ == "__main__":
    main()
