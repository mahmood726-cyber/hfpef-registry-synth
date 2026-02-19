# HFpEF Registry-First Transparency-Adjusted Synthesis

A reproducible Python project that builds a denominator-aware, transparency-adjusted, decision-grade synthesis for HFpEF RCTs from open registry results.

## Registry-First Philosophy
This engine uses trial registrations/protocols as the truth layer (denominator):
- Eligible HFpEF trial universe is defined first from ClinicalTrials.gov registrations.
- Missing results are treated as measurable reporting debt, not ignored.
- Synthesis is class-based with uncertainty and heterogeneity, not simplistic ranking.
- Outputs are decision-grade absolute effects per 1000 at configurable baseline risks.

## What It Produces
Running the main CLI generates:
- `outputs/trial_universe.csv`
- `outputs/results_extract_hfhosp.csv`
- `outputs/results_extract_sae.csv`
- `outputs/synthesis_decision_table.csv`
- `outputs/trust_capsules.csv`
- `outputs/mnar_envelopes.csv`
- `outputs/evidence_graph_edges.csv`
- `outputs/summary_report.md`
- `outputs/robustness_model_sensitivity.csv`
- `outputs/robustness_loo_sensitivity.csv`
- `outputs/validation_outcome_candidates.csv`
- `outputs/validation_adjudication_sample.csv`
- `outputs/validation_metrics.csv`
- `outputs/validation_misclassified.csv`
- `outputs/reporting_bias_framework_mapping.csv`
- `outputs/external_credibility_checks.csv`
- `outputs/runtime/reproducibility_manifest_latest.json`
- `outputs/runtime/reproducibility_snapshot_<UTC_TIMESTAMP>.tar.gz`

Additional helper outputs:
- class summaries, meta-regression coefficients, partial-pooling summaries, and graph node tables.

## Scope and Constraints
- HFpEF interventional trials, post-2015 default.
- Primary outcome focus: HF hospitalization.
- Safety focus: serious adverse events (SAE).
- No paywall bypass, no scraping non-API registries.
- Core data source: ClinicalTrials.gov v2 API (open). Optional PubMed/OpenAlex linkage is available via open APIs.

## Installation
```bash
cd /mnt/c/Users/user/hfpef_registry_synth
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## No-Sudo / No-Pip Fallback
If `pip` or root install is unavailable, bootstrap dependencies from Ubuntu packages into a local folder:
```bash
cd /mnt/c/Users/user/hfpef_registry_synth
./scripts/bootstrap_local_python_deps.sh /tmp/hfpydeps
source ./scripts/env_local_python.sh /tmp/hfpydeps
```

Then run commands with the same shell session (env vars already exported).

Or run a single command with wrapper:
```bash
./scripts/run_with_local_deps.sh python3 -m pytest -q
./scripts/run_with_local_deps.sh python3 -m scripts.run_hfpef --out_dir outputs --fixture_path tests/fixtures/mock_studies.json
```

## Run Full Pipeline
```bash
python3 -m scripts.run_hfpef \
  --out_dir outputs \
  --start_year 2015 \
  --grace_months 24 \
  --baseline_risks 50,100,200 \
  --validation_sample_size 40 \
  --use_pubmed false \
  --use_openalex false
```

Equivalent command format requested:
```bash
python -m scripts.run_hfpef --out_dir outputs --start_year 2015 --grace_months 24 --baseline_risks 50,100,200 --use_pubmed false --use_openalex false
```

## Export Graph Only
```bash
python3 -m scripts.export_graph --out_dir outputs
```

## Offline/Fixture Run (for tests and smoke)
```bash
python3 -m scripts.run_hfpef --out_dir outputs --fixture_path tests/fixtures/mock_studies.json
```

## Gold-Standard Adjudication Workflow
1. Generate candidate and sample files:
```bash
python3 -m scripts.run_hfpef --out_dir outputs --fixture_path tests/fixtures/mock_studies.json
```
2. Fill consensus labels in `outputs/validation_adjudication_sample.csv`.
3. Re-run with adjudication scoring:
```bash
python3 -m scripts.run_hfpef \
  --out_dir outputs \
  --adjudication_path outputs/validation_adjudication_sample.csv
```
4. Review:
- `outputs/validation_metrics.csv`
- `outputs/validation_misclassified.csv`

## Project Structure
- `src/hfpef_registry_synth/`
  - `ctgov_client.py` API + pagination + caching + retries/backoff
  - `universe.py` trial universe construction + EF extraction + class mapping
  - `results_extraction.py` HF hospitalization and SAE extraction with provenance
  - `synthesis.py` logRR, random effects, class partial pooling, meta-regression, decision table
  - `trust.py` denominator-aware trust capsules
- `mnar.py` transparency-adjusted MNAR sensitivity envelopes
- `robustness.py` alternative estimator + leave-one-out robustness checks
- `validation.py` adjudication candidate generation, sample templating, and accuracy metrics
- `framework_alignment.py` PRISMA/SW-iM/ROB-ME crosswalk exporter
- `credibility.py` external face-validity checks against known HFpEF class-level signals
- `reproducibility.py` frozen snapshot + manifest + archive packaging
  - `linkage.py` optional PubMed/OpenAlex publication linkage
  - `graph_export.py` field evidence graph exporter
  - `pipeline.py` full orchestration

Live-run efficiency note:
- The pipeline performs a shallow CT.gov query first, pre-filters eligibility, then hydrates only eligible records with posted results modules. This makes full live runs reproducible without hydrating the entire query universe.
- `scripts/`
  - `run_hfpef.py`
  - `export_graph.py`
- `tests/`
  - fixtures + parser/mapping/meta/smoke tests

## Configuration Knobs
- Baseline risks per 1000: `--baseline_risks`
- MNAR deltas (log-RR shifts for missing evidence): `--mnar_deltas`
- Grace window for reporting debt: `--grace_months`
- Clinical threshold for robustness checks: `--clinically_meaningful_arr`
- Validation sample size and seed: `--validation_sample_size`, `--validation_seed`
- Optional adjudication consensus CSV: `--adjudication_path`
- Toggle reproducibility packaging: `--build_repro_package true|false`

## Intervention Mapping
Edit class dictionaries in:
- `src/hfpef_registry_synth/mapping.py`

EF parsing and outcome harmonization rules are in:
- `src/hfpef_registry_synth/parsing.py`

## Interpreting Outputs
- `synthesis_decision_table.csv`: class-by-baseline absolute effect tradeoffs (HF hospitalization benefit vs SAE harm).
- `trust_capsules.csv`: explicit penalties and trust score components.
- `mnar_envelopes.csv`: shows whether conclusions remain stable when missing trials are assumed less favorable.
- `summary_report.md`: compact narrative of findings and robustness.
- `robustness_model_sensitivity.csv` / `robustness_loo_sensitivity.csv`: FE vs DL vs PM sensitivity and leave-one-out influence checks.
- `validation_*`: manual-adjudication candidate/sample files and scored misclassification metrics.
- `reporting_bias_framework_mapping.csv`: metric-by-metric mapping to PRISMA/SW-iM/ROB-ME.
- `external_credibility_checks.csv`: concordance against known HFpEF class-level directional signals.
- `outputs/runtime/reproducibility_manifest_latest.json`: run config, dependency versions, git fingerprint, and file hashes.
- `outputs/runtime/reproducibility_snapshot_<UTC_TIMESTAMP>.tar.gz`: frozen archive for fixed-date reproduction.
- SAE pooling uses participant-level totals (participants with >=1 SAE), drawn from total SAE term rows or `eventGroups.seriousNumAffected` when present; event-count-only SAE rows remain in extracts but are excluded from pooled RR synthesis.
- Pairwise synthesis excludes aggregate/non-contrast result groups (for example: `All Patients`, `Single Arm`, or pooled rows) to avoid unit-of-analysis contamination.
- HF hospitalization synthesis uses a strict direct endpoint rule and excludes composite/hierarchical, death-mixed, recurrent-event, clinical-worsening, and win-ratio outcomes to avoid mixing estimands.

## Limitations
- Registration outcomes may not be perfectly aligned to publication outcomes/timepoints.
- CT.gov result tables can vary (subjects vs events for SAE), and event-count-only SAE tables cannot be directly pooled as participant risk ratios.
- HR-only outcomes are not fully used in this MVP (binary arm-level counts prioritized).
- PubMed/OpenAlex linkage depends on public indexing; false negatives are possible for very recent or weakly indexed records.
- External credibility checks are face-validity anchors, not formal external validation.
- Manual adjudication metrics depend on quality and representativeness of the reviewed sample.

## Methods Documentation
- Statistical rationale: `docs/statistical_justification.md`
- Reporting-bias framework mapping: `docs/reporting_bias_alignment.md`
- Manual adjudication protocol: `docs/manual_adjudication_protocol.md`

## Legal / Ethical
- Uses only open APIs and open metadata.
- No paywall bypass.
- No scraping non-API registry systems.
