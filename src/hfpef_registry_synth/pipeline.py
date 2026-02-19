"""End-to-end pipeline orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd

from .config import PipelineConfig
from .credibility import run_external_credibility_checks
from .ctgov_client import CTGovClient
from .framework_alignment import build_framework_alignment_table
from .graph_export import build_evidence_graph
from .linkage import enrich_publication_flags
from .logging_utils import setup_logging
from .mnar import build_mnar_envelopes
from .reproducibility import create_reproducibility_package
from .report import write_summary_report
from .results_extraction import extract_results
from .robustness import run_model_robustness
from .synthesis import build_decision_table, build_pairwise_comparisons, run_class_synthesis
from .trust import build_trust_capsules
from .universe import TrialUniverseResult, build_trial_universe
from .validation import build_validation_outputs


@dataclass
class PipelineArtifacts:
    universe_df: pd.DataFrame
    hfhosp_extract_df: pd.DataFrame
    sae_extract_df: pd.DataFrame
    decision_df: pd.DataFrame
    trust_df: pd.DataFrame
    mnar_df: pd.DataFrame
    graph_edges_df: pd.DataFrame
    robustness_models_df: pd.DataFrame
    robustness_loo_df: pd.DataFrame
    validation_metrics_df: pd.DataFrame
    credibility_df: pd.DataFrame
    framework_alignment_df: pd.DataFrame


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
        logger.info("Querying CT.gov shallow records for eligibility pre-filter")
        shallow_studies = client.search_hfpef_trials(fetch_detail=False)
        provisional = build_trial_universe(shallow_studies, start_year=config.start_year)
        eligible_ids = set(provisional.df["nct_id"].astype(str).tolist()) if not provisional.df.empty else set()
        shallow_map = {
            (s.get("protocolSection", {}).get("identificationModule", {}).get("nctId", "") or "").upper(): s
            for s in shallow_studies
        }
        studies = []
        hydrated_count = 0
        for nct_id in sorted(eligible_ids):
            shallow = shallow_map.get(nct_id)
            if not shallow:
                continue
            if bool(shallow.get("hasResults")):
                try:
                    studies.append(client.fetch_study(nct_id))
                    hydrated_count += 1
                except Exception as exc:  # pragma: no cover - network behavior
                    logger.warning("Falling back to shallow eligible record for %s: %s", nct_id, exc)
                    studies.append(shallow)
            else:
                studies.append(shallow)
        logger.info(
            "Eligible pre-filtered trials: %d (hydrated for results modules: %d)",
            len(studies),
            hydrated_count,
        )
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

    adjudication_df = None
    if config.adjudication_path:
        adjudication_path = Path(config.adjudication_path)
        if not adjudication_path.exists():
            raise FileNotFoundError(f"Adjudication file not found: {adjudication_path}")
        adjudication_df = pd.read_csv(adjudication_path)

    logger.info("Building manual-adjudication validation package")
    validation = build_validation_outputs(
        studies=universe_res.study_index,
        sample_size_per_domain=config.validation_sample_size,
        seed=config.validation_seed,
        adjudication_df=adjudication_df,
    )
    _save(validation.candidates_df, config.out_dir / "validation_outcome_candidates.csv")
    _save(validation.sample_df, config.out_dir / "validation_adjudication_sample.csv")
    _save(validation.metrics_df, config.out_dir / "validation_metrics.csv")
    _save(validation.misclassified_df, config.out_dir / "validation_misclassified.csv")

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

    logger.info("Running robustness checks across meta-analytic specifications")
    robustness_models_df, robustness_loo_df = run_model_robustness(all_comp_df)
    _save(robustness_models_df, config.out_dir / "robustness_model_sensitivity.csv")
    _save(robustness_loo_df, config.out_dir / "robustness_loo_sensitivity.csv")

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

    logger.info("Running external face-validity checks")
    credibility_df = run_external_credibility_checks(hfhosp_summary, sae_summary)
    _save(credibility_df, config.out_dir / "external_credibility_checks.csv")

    logger.info("Building PRISMA/SW-iM/ROB-ME framework mapping")
    framework_df = build_framework_alignment_table(trust_df, mnar_df)
    _save(framework_df, config.out_dir / "reporting_bias_framework_mapping.csv")

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
        robustness_models_df=robustness_models_df,
        robustness_loo_df=robustness_loo_df,
        validation_metrics_df=validation.metrics_df,
        credibility_df=credibility_df,
        framework_df=framework_df,
    )

    if config.build_repro_package:
        logger.info("Creating reproducibility snapshot package")
        package_outputs = [
            config.out_dir / "trial_universe.csv",
            config.out_dir / "results_extract_hfhosp.csv",
            config.out_dir / "results_extract_sae.csv",
            config.out_dir / "study_effects_hfhosp.csv",
            config.out_dir / "study_effects_sae.csv",
            config.out_dir / "synthesis_hfhosp_class_summary.csv",
            config.out_dir / "synthesis_sae_class_summary.csv",
            config.out_dir / "meta_regression_hfhosp.csv",
            config.out_dir / "meta_regression_sae.csv",
            config.out_dir / "partial_pooling_hfhosp.csv",
            config.out_dir / "partial_pooling_sae.csv",
            config.out_dir / "robustness_model_sensitivity.csv",
            config.out_dir / "robustness_loo_sensitivity.csv",
            config.out_dir / "synthesis_decision_table.csv",
            config.out_dir / "trust_capsules.csv",
            config.out_dir / "mnar_envelopes.csv",
            config.out_dir / "external_credibility_checks.csv",
            config.out_dir / "reporting_bias_framework_mapping.csv",
            config.out_dir / "validation_outcome_candidates.csv",
            config.out_dir / "validation_adjudication_sample.csv",
            config.out_dir / "validation_metrics.csv",
            config.out_dir / "validation_misclassified.csv",
            config.out_dir / "evidence_graph_edges.csv",
            config.out_dir / "evidence_graph_nodes_trials.csv",
            config.out_dir / "evidence_graph_nodes_intervention_classes.csv",
            config.out_dir / "summary_report.md",
        ]
        create_reproducibility_package(
            config=config,
            output_files=package_outputs,
            command=config.run_command or "python3 -m scripts.run_hfpef",
        )

    return PipelineArtifacts(
        universe_df=universe_df,
        hfhosp_extract_df=extracted.hfhosp_df,
        sae_extract_df=extracted.sae_df,
        decision_df=decision_df,
        trust_df=trust_df,
        mnar_df=mnar_df,
        graph_edges_df=graph.edges,
        robustness_models_df=robustness_models_df,
        robustness_loo_df=robustness_loo_df,
        validation_metrics_df=validation.metrics_df,
        credibility_df=credibility_df,
        framework_alignment_df=framework_df,
    )
