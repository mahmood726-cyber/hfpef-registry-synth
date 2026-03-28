# HFpEF Registry-First Transparency-Adjusted Synthesis

Generated: 2026-02-19 21:54 UTC

## Registry-First Principle
This report treats trial registrations/protocols as the denominator truth layer and explicitly accounts for missing results as measurable reporting debt.

## Run Configuration
- start_year: 2015
- grace_months: 24
- baseline_risks_per_1000: 50,100,200
- mnar_deltas: 0.0,0.1,0.2
- use_pubmed: False
- use_openalex: False

## Trial Universe Snapshot
- Eligible HFpEF interventional trials: 4
- Completed trials: 4
- Trials with posted CT.gov results module: 3
- Trials with publication linkage (PubMed/OpenAlex): 0

## HF Hospitalization Synthesis (Class-level)
- intervention_class=ARNI, k_studies=1, pooled_rr=0.875, ci_low_rr=0.6051680612990534, ci_high_rr=1.2651444267506613, i2=0.0
- intervention_class=MRA, k_studies=1, pooled_rr=0.8799999999999999, ci_low_rr=0.5375703099388714, ci_high_rr=1.4405557481179698, i2=0.0
- intervention_class=SGLT2 inhibitors, k_studies=1, pooled_rr=0.6666666666666667, ci_low_rr=0.4070900121658477, ci_high_rr=1.0917596383164976, i2=0.0


## SAE Synthesis (Class-level)
- intervention_class=ARNI, k_studies=1, pooled_rr=1.142857142857143, ci_low_rr=0.5866707802423063, ci_high_rr=2.226329472962908, i2=0.0
- intervention_class=MRA, k_studies=1, pooled_rr=1.2000000000000002, ci_low_rr=0.645658298651167, ci_high_rr=2.230281873567301, i2=0.0
- intervention_class=SGLT2 inhibitors, k_studies=1, pooled_rr=0.8333333333333334, ci_low_rr=0.3774013284222466, ci_high_rr=1.840068892570197, i2=0.0


## Decision-Grade Absolute Effects (per 1000)
- intervention_class=ARNI, baseline_risk_per_1000=50, arr_hfhosp_per_1000=6.25, ari_sae_per_1000=7.142857142857153, net_benefit_per_1000=-0.892857142857153
- intervention_class=ARNI, baseline_risk_per_1000=100, arr_hfhosp_per_1000=12.5, ari_sae_per_1000=14.285714285714306, net_benefit_per_1000=-1.785714285714306
- intervention_class=ARNI, baseline_risk_per_1000=200, arr_hfhosp_per_1000=25.0, ari_sae_per_1000=28.571428571428612, net_benefit_per_1000=-3.571428571428612
- intervention_class=MRA, baseline_risk_per_1000=50, arr_hfhosp_per_1000=6.000000000000007, ari_sae_per_1000=10.000000000000007, net_benefit_per_1000=-4.0
- intervention_class=MRA, baseline_risk_per_1000=100, arr_hfhosp_per_1000=12.000000000000014, ari_sae_per_1000=20.000000000000014, net_benefit_per_1000=-8.0
- intervention_class=MRA, baseline_risk_per_1000=200, arr_hfhosp_per_1000=24.00000000000003, ari_sae_per_1000=40.00000000000003, net_benefit_per_1000=-16.0
- intervention_class=SGLT2 inhibitors, baseline_risk_per_1000=50, arr_hfhosp_per_1000=16.666666666666664, ari_sae_per_1000=-8.333333333333329, net_benefit_per_1000=24.999999999999993
- intervention_class=SGLT2 inhibitors, baseline_risk_per_1000=100, arr_hfhosp_per_1000=33.33333333333333, ari_sae_per_1000=-16.666666666666657, net_benefit_per_1000=49.999999999999986


## Trust Capsules
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, ecr_trials=1.0, ecr_participants=1.0, reporting_debt_rate=0.0, trust_score=85
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, ecr_trials=1.0, ecr_participants=1.0, reporting_debt_rate=0.0, trust_score=85
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, ecr_trials=0.5, ecr_participants=0.5555555555555556, reporting_debt_rate=0.5, trust_score=40
- intervention_class=ARNI, outcome=SAE, ecr_trials=1.0, ecr_participants=1.0, reporting_debt_rate=0.0, trust_score=85
- intervention_class=MRA, outcome=SAE, ecr_trials=1.0, ecr_participants=1.0, reporting_debt_rate=0.0, trust_score=85
- intervention_class=SGLT2 inhibitors, outcome=SAE, ecr_trials=0.5, ecr_participants=0.5555555555555556, reporting_debt_rate=0.5, trust_score=40


## MNAR Transparency-Adjusted Sensitivity
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, scenario=S0_MAR, observed_rr=0.875, adjusted_rr=0.875, conclusion_change=stable, robust_under_scenario=True
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, scenario=delta_+0.10, observed_rr=0.875, adjusted_rr=0.875, conclusion_change=stable, robust_under_scenario=True
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, scenario=delta_+0.20, observed_rr=0.875, adjusted_rr=0.875, conclusion_change=stable, robust_under_scenario=True
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, scenario=S0_MAR, observed_rr=0.8799999999999999, adjusted_rr=0.8799999999999999, conclusion_change=stable, robust_under_scenario=True
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, scenario=delta_+0.10, observed_rr=0.8799999999999999, adjusted_rr=0.8799999999999999, conclusion_change=stable, robust_under_scenario=True
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, scenario=delta_+0.20, observed_rr=0.8799999999999999, adjusted_rr=0.8799999999999999, conclusion_change=stable, robust_under_scenario=True
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, scenario=S0_MAR, observed_rr=0.6666666666666667, adjusted_rr=0.6666666666666667, conclusion_change=stable, robust_under_scenario=True
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, scenario=delta_+0.10, observed_rr=0.6666666666666667, adjusted_rr=0.6969645964760282, conclusion_change=stable, robust_under_scenario=True


## Statistical Robustness (Model and Influence)
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, method=DL, pooled_rr=0.875, ci_low_rr=0.6051680612990534, ci_high_rr=1.2651444267506613, direction=uncertain
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, method=FE, pooled_rr=0.875, ci_low_rr=0.6051680612990534, ci_high_rr=1.2651444267506613, direction=uncertain
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, method=PM, pooled_rr=0.875, ci_low_rr=0.6051680612990534, ci_high_rr=1.2651444267506613, direction=uncertain
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, method=DL, pooled_rr=0.8799999999999999, ci_low_rr=0.5375703099388713, ci_high_rr=1.4405557481179698, direction=uncertain
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, method=FE, pooled_rr=0.8799999999999999, ci_low_rr=0.5375703099388713, ci_high_rr=1.4405557481179698, direction=uncertain
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, method=PM, pooled_rr=0.8799999999999999, ci_low_rr=0.5375703099388713, ci_high_rr=1.4405557481179698, direction=uncertain
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, method=DL, pooled_rr=0.6666666666666667, ci_low_rr=0.4070900121658477, ci_high_rr=1.0917596383164976, direction=uncertain
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, method=FE, pooled_rr=0.6666666666666667, ci_low_rr=0.4070900121658477, ci_high_rr=1.0917596383164976, direction=uncertain

- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, direction_concordant_across_methods=True, max_abs_rr_shift_vs_dl=0.0, loo_crosses_null=False, robustness_flag=True
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, direction_concordant_across_methods=True, max_abs_rr_shift_vs_dl=0.0, loo_crosses_null=False, robustness_flag=True
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, direction_concordant_across_methods=True, max_abs_rr_shift_vs_dl=0.0, loo_crosses_null=False, robustness_flag=True
- intervention_class=ARNI, outcome=SAE, direction_concordant_across_methods=True, max_abs_rr_shift_vs_dl=0.0, loo_crosses_null=False, robustness_flag=True
- intervention_class=MRA, outcome=SAE, direction_concordant_across_methods=True, max_abs_rr_shift_vs_dl=0.0, loo_crosses_null=False, robustness_flag=True
- intervention_class=SGLT2 inhibitors, outcome=SAE, direction_concordant_across_methods=True, max_abs_rr_shift_vs_dl=0.0, loo_crosses_null=False, robustness_flag=True


## Manual Adjudication Validation
- domain=HF_HOSPITALIZATION, n_reviewed=3, accuracy=1.0, sensitivity=1.0, specificity=nan, misclassification_rate=0.0, status=scored_from_consensus_labels
- domain=SAE, n_reviewed=3, accuracy=1.0, sensitivity=nan, specificity=1.0, misclassification_rate=0.0, status=scored_from_consensus_labels


## External Face-Validity Checks
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, expected_direction=uncertain_or_small_benefit, observed_direction=uncertain, concordance=full_concordance
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, expected_direction=uncertain_or_small_benefit, observed_direction=uncertain, concordance=full_concordance
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, expected_direction=benefit, observed_direction=uncertain, concordance=partial_concordance
- intervention_class=SGLT2 inhibitors, outcome=SAE, expected_direction=neutral_or_benefit, observed_direction=uncertain, concordance=full_concordance


## Reporting-Bias Framework Alignment
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, metric=ecr_participants, value=1.0, framework=SWiM, framework_item=Item 5/6 (synthesis grouping and data contribution)
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, metric=ecr_trials, value=1.0, framework=SWiM, framework_item=Item 5/6 (synthesis grouping and data contribution)
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, metric=eligible_completed_trials, value=1, framework=PRISMA 2020, framework_item=Item 16a (study selection)
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, metric=endpoint_alignment_rate, value=1.0, framework=SWiM, framework_item=Item 7 (standardised metric and comparability)
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, metric=heterogeneity_i2, value=0.0, framework=PRISMA 2020, framework_item=Item 20b/20d (results of syntheses, heterogeneity)
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, metric=mnar_robust_under_scenario, value=True, framework=ROB-ME, framework_item=Sensitivity analysis under plausible missing evidence
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, metric=reporting_debt_rate, value=0.0, framework=ROB-ME, framework_item=Risk due to missing results
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, metric=ecr_participants, value=1.0, framework=SWiM, framework_item=Item 5/6 (synthesis grouping and data contribution)


## Interpretation Notes
- No SUCRA or ordinal ranking is produced.
- Decision support is expressed as absolute effects and net tradeoffs with uncertainty.
- Trust score is explicit and editable, not a black-box model.
- Robustness tables compare fixed-effect, DL random-effects, and Paule-Mandel random-effects estimates with leave-one-out stress tests.
- Validation metrics are scored against manually adjudicated consensus labels when provided; otherwise templates are generated for reviewer completion.
- Reporting-bias alignment table links each transparency metric to PRISMA/SW-iM/ROB-ME reporting domains.

## Known Limitations
- Registry outcomes may not align exactly with publication endpoint definitions.
- Missing PDFs and non-posted results remain partially unobserved by design.
- SAE synthesis uses participant-level totals where available (total SAE rows or event-group serious totals); event-count-only SAE tables are flagged and excluded from pooled RR.
