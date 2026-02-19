# Statistical Justification and Robustness Plan

## Primary Estimand
- Contrast-level risk ratio (RR) for binary outcomes:
  - HF hospitalization
  - serious adverse events (participants with >=1 SAE)
- Study-level effect uses log(RR) with continuity correction when needed.

## Primary Synthesis Model
- Class-based random-effects meta-analysis using DerSimonian-Laird (DL) tau^2.
- Drug-level partial pooling inside class:
  - estimate drug-specific effects,
  - shrink toward class mean with between-drug variance.
- Meta-regression modifiers:
  - baseline control event risk (CER),
  - EF band,
  - primary completion year.

## Why This Model
- Registry-first extraction yields sparse and heterogeneous evidence per class.
- Class partial pooling reduces over-interpretation of single-drug sparse contrasts.
- Random-effects framework explicitly acknowledges between-study variability.
- Meta-regression keeps effect-modification assumptions simple and auditable.

## Alternative Specifications (Implemented)
- Fixed-effect model (FE).
- Random-effects with DL tau^2.
- Random-effects with Paule-Mandel (PM) tau^2.
- Leave-one-out DL influence checks.

These are exported to:
- `outputs/robustness_model_sensitivity.csv`
- `outputs/robustness_loo_sensitivity.csv`

## Robustness Interpretation Rule
- Direction-concordant across FE/DL/PM and no leave-one-out null crossing:
  - `robustness_flag = true`
- Otherwise:
  - estimate considered model-sensitive or influence-sensitive.

## Why Not Full Bayesian in This MVP
- Objective was a lightweight, reproducible stack with minimal dependencies.
- Bayesian hierarchical NMA could be added later, but would require:
  - explicit prior sensitivity,
  - convergence diagnostics,
  - heavier runtime/dependency footprint.
- Current robustness suite provides transparent frequentist triangulation.
