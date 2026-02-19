# Reporting-Bias Framework Alignment

This project maps denominator-aware trust and transparency metrics to established synthesis/reporting frameworks.

## Framework Crosswalk

1. PRISMA 2020
- Eligible/completed denominator metrics (`eligible_completed_trials`) align with study selection and synthesis reporting expectations.
- Heterogeneity reporting (`heterogeneity_i2`) aligns with synthesis result uncertainty reporting.

2. SWiM
- Evidence contribution ratios (`ecr_trials`, `ecr_participants`) align with transparent reporting of study contribution to each synthesis.
- Endpoint alignment (`endpoint_alignment_rate`) aligns with comparability and synthesis-standardization reporting.

3. ROB-ME (risk of bias due to missing evidence)
- Reporting debt (`reporting_debt_rate`) operationalizes risk due to missing results among completed studies.
- MNAR sensitivity robustness (`mnar_robust_under_scenario`) operationalizes plausible missing-not-at-random stress testing.

## Operational Output

The mapping is exported per class/outcome to:
- `outputs/reporting_bias_framework_mapping.csv`

This file is intentionally explicit and editable so reviewers can trace each metric to a framework concept and challenge thresholds if needed.
