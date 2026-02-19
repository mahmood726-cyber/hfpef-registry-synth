"""End-to-end pipeline orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd

from .config import PipelineConfig
from .ctgov_client import CTGovClient
from .graph_export import build_evidence_graph
from .linkage import enrich_publication_flags
from .logging_utils import setup_logging
from .mnar import build_mnar_envelopes
from .report import write_summary_report
from .results_extraction import extract_results
from .synthesis import build_decision_table, build_pairwise_comparisons, run_class_synthesis
from .trust import build_trust_capsules
from .universe import TrialUniverseResult, build_trial_universe


@dataclass
class PipelineArtifacts:
    universe_df: pd.DataFrame
    hfhosp_extract_df: pd.DataFrame
    sae_extract_df: pd.DataFrame
    decision_df: pd.DataFrame
    trust_df: pd.DataFrame
    mnar_df: pd.DataFrame
    graph_edges_df: pd.DataFrame


def _ensure_output_dirs(config: PipelineConfig) -> None:
    config.ensure_dirs()
    (config.out_dir / "runtime").mkdir(parents=True, exist_ok=True)


def _save(df: pd.DataFrame, path: Path) -> None:
    if df is None:
        pd.DataFrame().to_csv(path, index=False)
        return
    df.to_csv(path, index=False)


def run_pipeline(config: PipelineConfig, preloaded_studies: Optional[Iterable[Dict]] = None) -> PipelineArtifacts:
    _ensure_output_dirs(config)
    logger = setup_logging(name="hfpef_registry_synth.pipeline")

    if preloaded_studies is None:
        client = CTGovClient(
            cache_dir=config.cache_dir,
            timeout=config.request_timeout,
            max_retries=config.max_retries,
            sleep_seconds=config.sleep_seconds,
        )
        studies = client.search_hfpef_trials(fetch_detail=True)
    else:
        studies = list(preloaded_studies)

    logger.info("Building trial universe from %d fetched studies", len(studies))
    universe_res: TrialUniverseResult = build_trial_universe(studies, start_year=config.start_year)
    universe_df = enrich_publication_flags(
        universe_df=universe_res.df,
        cache_dir=config.cache_dir,
        use_pubmed=config.use_pubmed,
        use_openalex=config.use_openalex,
        timeout=config.request_timeout,
        max_retries=config.max_retries,
        sleep_seconds=config.sleep_seconds,
    )

    universe_path = config.out_dir / "trial_universe.csv"
    _save(universe_df, universe_path)

    trial_meta_map = universe_df.set_index("nct_id").to_dict(orient="index") if not universe_df.empty else {}
    logger.info("Extracting outcome results from CT.gov results modules")
    extracted = extract_results(universe_res.study_index, trial_meta_map)

    hfhosp_extract_path = config.out_dir / "results_extract_hfhosp.csv"
    sae_extract_path = config.out_dir / "results_extract_sae.csv"
    _save(extracted.hfhosp_df, hfhosp_extract_path)
    _save(extracted.sae_df, sae_extract_path)

    logger.info("Building study-level comparisons")
    hfhosp_comp_df = build_pairwise_comparisons(
        extracted.hfhosp_df,
        universe_df,
        event_col="events",
        outcome_label="HF_HOSPITALIZATION",
    )
    sae_subject_df = extracted.sae_df
    if not sae_subject_df.empty and "count_type" in sae_subject_df.columns:
        total_rows = len(sae_subject_df)
        sae_subject_df = sae_subject_df[sae_subject_df["count_type"] == "subjects_with_>=1_sae"].copy()
        logger.info(
            "SAE synthesis uses participant-level totals only: retained %d/%d arm rows",
            len(sae_subject_df),
            total_rows,
        )

    sae_comp_df = build_pairwise_comparisons(
        sae_subject_df,
        universe_df,
        event_col="subjects_with_sae",
        outcome_label="SAE",
    )

    _save(hfhosp_comp_df, config.out_dir / "study_effects_hfhosp.csv")
    _save(sae_comp_df, config.out_dir / "study_effects_sae.csv")

    all_comp_df = pd.concat([hfhosp_comp_df, sae_comp_df], ignore_index=True) if not (hfhosp_comp_df.empty and sae_comp_df.empty) else pd.DataFrame()

    logger.info("Running class-based synthesis")
    hfhosp_summary, hfhosp_reg, hfhosp_shrink = run_class_synthesis(all_comp_df, "HF_HOSPITALIZATION")
    sae_summary, sae_reg, sae_shrink = run_class_synthesis(all_comp_df, "SAE")

    _save(hfhosp_summary, config.out_dir / "synthesis_hfhosp_class_summary.csv")
    _save(sae_summary, config.out_dir / "synthesis_sae_class_summary.csv")
    _save(hfhosp_reg, config.out_dir / "meta_regression_hfhosp.csv")
    _save(sae_reg, config.out_dir / "meta_regression_sae.csv")
    _save(hfhosp_shrink, config.out_dir / "partial_pooling_hfhosp.csv")
    _save(sae_shrink, config.out_dir / "partial_pooling_sae.csv")

    decision_df = build_decision_table(hfhosp_summary, sae_summary, baseline_risks=config.baseline_risks)
    _save(decision_df, config.out_dir / "synthesis_decision_table.csv")

    logger.info("Building trust capsules")
    trust_df = build_trust_capsules(
        universe_df=universe_df,
        hfhosp_comp_df=hfhosp_comp_df,
        sae_comp_df=sae_comp_df,
        hfhosp_summary=hfhosp_summary,
        sae_summary=sae_summary,
        grace_months=config.grace_months,
    )
    _save(trust_df, config.out_dir / "trust_capsules.csv")

    logger.info("Building MNAR sensitivity envelopes")
    baseline_med = config.baseline_risks[len(config.baseline_risks) // 2] if config.baseline_risks else 100
    mnar_hf = build_mnar_envelopes(
        universe_df=universe_df,
        comparisons_df=hfhosp_comp_df,
        summary_df=hfhosp_summary,
        outcome="HF_HOSPITALIZATION",
        deltas=config.mnar_deltas,
        baseline_risk_per_1000=baseline_med,
        clinically_meaningful_arr=config.clinically_meaningful_arr,
    )
    mnar_sae = build_mnar_envelopes(
        universe_df=universe_df,
        comparisons_df=sae_comp_df,
        summary_df=sae_summary,
        outcome="SAE",
        deltas=config.mnar_deltas,
        baseline_risk_per_1000=baseline_med,
        clinically_meaningful_arr=config.clinically_meaningful_arr,
    )
    mnar_df = pd.concat([mnar_hf, mnar_sae], ignore_index=True) if not (mnar_hf.empty and mnar_sae.empty) else pd.DataFrame()
    _save(mnar_df, config.out_dir / "mnar_envelopes.csv")

    logger.info("Exporting evidence graph")
    graph = build_evidence_graph(universe_df, extracted.hfhosp_df, extracted.sae_df)
    _save(graph.edges, config.out_dir / "evidence_graph_edges.csv")
    _save(graph.trial_nodes, config.out_dir / "evidence_graph_nodes_trials.csv")
    _save(graph.class_nodes, config.out_dir / "evidence_graph_nodes_intervention_classes.csv")

    logger.info("Writing markdown summary report")
    write_summary_report(
        path=config.out_dir / "summary_report.md",
        config=config,
        universe_df=universe_df,
        hfhosp_summary=hfhosp_summary,
        sae_summary=sae_summary,
        decision_df=decision_df,
        trust_df=trust_df,
        mnar_df=mnar_df,
    )

    return PipelineArtifacts(
        universe_df=universe_df,
        hfhosp_extract_df=extracted.hfhosp_df,
        sae_extract_df=extracted.sae_df,
        decision_df=decision_df,
        trust_df=trust_df,
        mnar_df=mnar_df,
        graph_edges_df=graph.edges,
    )
