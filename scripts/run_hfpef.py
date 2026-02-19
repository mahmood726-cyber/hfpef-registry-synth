"""CLI: run full HFpEF registry-first synthesis pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, List
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hfpef_registry_synth.config import (
    PipelineConfig,
    normalize_baseline_risks,
    parse_bool,
    parse_float_list,
    parse_int_list,
)
from hfpef_registry_synth.logging_utils import setup_logging
from hfpef_registry_synth.pipeline import run_pipeline


def _load_fixture(path: str) -> List[Any]:
    if not path:
        return []
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "studies" in payload:
        return payload["studies"]
    if isinstance(payload, list):
        return payload
    raise ValueError("Fixture must be a list of studies or object with 'studies'.")


def main() -> None:
    parser = argparse.ArgumentParser(description="HFpEF registry-first, transparency-adjusted synthesis")
    parser.add_argument("--out_dir", default="outputs", help="Output directory")
    parser.add_argument("--cache_dir", default="cache", help="Cache directory")
    parser.add_argument("--start_year", type=int, default=2015)
    parser.add_argument("--grace_months", type=int, default=24)
    parser.add_argument("--baseline_risks", default="50,100,200")
    parser.add_argument("--mnar_deltas", default="0.0,0.10,0.20")
    parser.add_argument("--use_pubmed", default="false")
    parser.add_argument("--use_openalex", default="false")
    parser.add_argument("--clinically_meaningful_arr", type=float, default=10.0)
    parser.add_argument("--fixture_path", default="", help="Optional local JSON fixture (offline mode)")

    args = parser.parse_args()
    logger = setup_logging(name="hfpef_registry_synth.cli")

    baseline_risks = normalize_baseline_risks(parse_int_list(args.baseline_risks, [50, 100, 200]))
    mnar_deltas = parse_float_list(args.mnar_deltas, [0.0, 0.10, 0.20])

    config = PipelineConfig(
        out_dir=Path(args.out_dir),
        cache_dir=Path(args.cache_dir),
        start_year=args.start_year,
        grace_months=args.grace_months,
        baseline_risks=baseline_risks,
        mnar_deltas=mnar_deltas,
        use_pubmed=parse_bool(args.use_pubmed, False),
        use_openalex=parse_bool(args.use_openalex, False),
        clinically_meaningful_arr=args.clinically_meaningful_arr,
    )

    fixture = _load_fixture(args.fixture_path) if args.fixture_path else None
    artifacts = run_pipeline(config=config, preloaded_studies=fixture)

    logger.info("Run complete.")
    logger.info("Universe trials: %d", len(artifacts.universe_df))
    logger.info("HF hospitalization extract rows: %d", len(artifacts.hfhosp_extract_df))
    logger.info("SAE extract rows: %d", len(artifacts.sae_extract_df))
    logger.info("Decision rows: %d", len(artifacts.decision_df))


if __name__ == "__main__":
    main()
