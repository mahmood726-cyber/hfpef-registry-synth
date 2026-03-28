# HFpEF Registry-First Transparency-Adjusted Synthesis

Generated: 2026-02-19 22:09 UTC

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
- Eligible HFpEF interventional trials: 410
- Completed trials: 151
- Trials with posted CT.gov results module: 72
- Trials with publication linkage (PubMed/OpenAlex): 0

## HF Hospitalization Synthesis (Class-level)
- intervention_class=Other, k_studies=1, pooled_rr=0.4, ci_low_rr=0.0283223247541003, ci_high_rr=5.649253773803874, i2=0.0


## SAE Synthesis (Class-level)
- intervention_class=ARB/ACEi, k_studies=1, pooled_rr=0.8122362869198313, ci_low_rr=0.19925181422599772, ci_high_rr=3.3110252388519297, i2=0.0
- intervention_class=MRA, k_studies=1, pooled_rr=0.953833470733718, ci_low_rr=0.8959431560704028, ci_high_rr=1.0154643000815993, i2=0.0
- intervention_class=Other, k_studies=24, pooled_rr=1.011955618538825, ci_low_rr=0.9694027628855695, ci_high_rr=1.0563763722356727, i2=21.24588289889892
- intervention_class=SGLT2 inhibitors, k_studies=7, pooled_rr=0.9840563237575861, ci_low_rr=0.8819308128584681, ci_high_rr=1.098007728280493, i2=37.38148390763857
- intervention_class=sGC stimulators, k_studies=3, pooled_rr=1.03382674974074, ci_low_rr=0.8116922492663428, ci_high_rr=1.3167524384340836, i2=0.0


## Decision-Grade Absolute Effects (per 1000)
- intervention_class=ARB/ACEi, baseline_risk_per_1000=50, arr_hfhosp_per_1000=nan, ari_sae_per_1000=-9.388185654008439, net_benefit_per_1000=nan
- intervention_class=ARB/ACEi, baseline_risk_per_1000=100, arr_hfhosp_per_1000=nan, ari_sae_per_1000=-18.776371308016877, net_benefit_per_1000=nan
- intervention_class=ARB/ACEi, baseline_risk_per_1000=200, arr_hfhosp_per_1000=nan, ari_sae_per_1000=-37.552742616033754, net_benefit_per_1000=nan
- intervention_class=MRA, baseline_risk_per_1000=50, arr_hfhosp_per_1000=nan, ari_sae_per_1000=-2.3083264633140956, net_benefit_per_1000=nan
- intervention_class=MRA, baseline_risk_per_1000=100, arr_hfhosp_per_1000=nan, ari_sae_per_1000=-4.616652926628191, net_benefit_per_1000=nan
- intervention_class=MRA, baseline_risk_per_1000=200, arr_hfhosp_per_1000=nan, ari_sae_per_1000=-9.233305853256383, net_benefit_per_1000=nan
- intervention_class=Other, baseline_risk_per_1000=50, arr_hfhosp_per_1000=30.0, ari_sae_per_1000=0.5977809269412475, net_benefit_per_1000=29.402219073058752
- intervention_class=Other, baseline_risk_per_1000=100, arr_hfhosp_per_1000=60.0, ari_sae_per_1000=1.195561853882495, net_benefit_per_1000=58.804438146117505


## Trust Capsules
- intervention_class=ARB/ACEi, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.25, trust_score=50
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.14285714285714285, trust_score=60
- intervention_class=Beta blockers, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.0, trust_score=60
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.0, trust_score=60
- intervention_class=Neprilysin inhibitors, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.0, trust_score=60
- intervention_class=Other, outcome=HF_HOSPITALIZATION, ecr_trials=0.007936507936507936, ecr_participants=0.002018018018018018, reporting_debt_rate=0.5961538461538461, trust_score=40
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.2, trust_score=50
- intervention_class=Unknown, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.0, trust_score=60


## MNAR Transparency-Adjusted Sensitivity
- intervention_class=Other, outcome=HF_HOSPITALIZATION, scenario=S0_MAR, observed_rr=0.4, adjusted_rr=0.4, conclusion_change=stable, robust_under_scenario=True
- intervention_class=Other, outcome=HF_HOSPITALIZATION, scenario=delta_+0.10, observed_rr=0.4, adjusted_rr=0.44196960983503375, conclusion_change=stable, robust_under_scenario=True
- intervention_class=Other, outcome=HF_HOSPITALIZATION, scenario=delta_+0.20, observed_rr=0.4, adjusted_rr=0.48834284004432993, conclusion_change=stable, robust_under_scenario=True
- intervention_class=ARB/ACEi, outcome=SAE, scenario=S0_MAR, observed_rr=0.8122362869198313, adjusted_rr=0.8122362869198313, conclusion_change=stable, robust_under_scenario=True
- intervention_class=ARB/ACEi, outcome=SAE, scenario=delta_+0.10, observed_rr=0.8122362869198313, adjusted_rr=0.8932518812990693, conclusion_change=stable, robust_under_scenario=True
- intervention_class=ARB/ACEi, outcome=SAE, scenario=delta_+0.20, observed_rr=0.8122362869198313, adjusted_rr=0.9823482849678201, conclusion_change=stable, robust_under_scenario=True
- intervention_class=MRA, outcome=SAE, scenario=S0_MAR, observed_rr=0.953833470733718, adjusted_rr=0.953833470733718, conclusion_change=stable, robust_under_scenario=True
- intervention_class=MRA, outcome=SAE, scenario=delta_+0.10, observed_rr=0.953833470733718, adjusted_rr=0.953833470733718, conclusion_change=stable, robust_under_scenario=True


## Statistical Robustness (Model and Influence)
- intervention_class=Other, outcome=HF_HOSPITALIZATION, method=DL, pooled_rr=0.39999999999999997, ci_low_rr=0.0283223247541003, ci_high_rr=5.649253773803874, direction=uncertain
- intervention_class=Other, outcome=HF_HOSPITALIZATION, method=FE, pooled_rr=0.39999999999999997, ci_low_rr=0.0283223247541003, ci_high_rr=5.649253773803874, direction=uncertain
- intervention_class=Other, outcome=HF_HOSPITALIZATION, method=PM, pooled_rr=0.39999999999999997, ci_low_rr=0.0283223247541003, ci_high_rr=5.649253773803874, direction=uncertain
- intervention_class=ARB/ACEi, outcome=SAE, method=DL, pooled_rr=0.8122362869198313, ci_low_rr=0.19925181422599772, ci_high_rr=3.3110252388519297, direction=uncertain
- intervention_class=ARB/ACEi, outcome=SAE, method=FE, pooled_rr=0.8122362869198313, ci_low_rr=0.19925181422599772, ci_high_rr=3.3110252388519297, direction=uncertain
- intervention_class=ARB/ACEi, outcome=SAE, method=PM, pooled_rr=0.8122362869198313, ci_low_rr=0.19925181422599772, ci_high_rr=3.3110252388519297, direction=uncertain
- intervention_class=MRA, outcome=SAE, method=DL, pooled_rr=0.953833470733718, ci_low_rr=0.8959431560704028, ci_high_rr=1.0154643000815993, direction=uncertain
- intervention_class=MRA, outcome=SAE, method=FE, pooled_rr=0.953833470733718, ci_low_rr=0.8959431560704028, ci_high_rr=1.0154643000815993, direction=uncertain

- intervention_class=Other, outcome=HF_HOSPITALIZATION, direction_concordant_across_methods=True, max_abs_rr_shift_vs_dl=0.0, loo_crosses_null=False, robustness_flag=True
- intervention_class=ARB/ACEi, outcome=SAE, direction_concordant_across_methods=True, max_abs_rr_shift_vs_dl=0.0, loo_crosses_null=False, robustness_flag=True
- intervention_class=MRA, outcome=SAE, direction_concordant_across_methods=True, max_abs_rr_shift_vs_dl=0.0, loo_crosses_null=False, robustness_flag=True
- intervention_class=Other, outcome=SAE, direction_concordant_across_methods=True, max_abs_rr_shift_vs_dl=0.02392048311277828, loo_crosses_null=True, robustness_flag=False
- intervention_class=SGLT2 inhibitors, outcome=SAE, direction_concordant_across_methods=False, max_abs_rr_shift_vs_dl=0.015838845085453745, loo_crosses_null=False, robustness_flag=False
- intervention_class=sGC stimulators, outcome=SAE, direction_concordant_across_methods=True, max_abs_rr_shift_vs_dl=0.0, loo_crosses_null=False, robustness_flag=True


## Manual Adjudication Validation
- domain=HF_HOSPITALIZATION, n_reviewed=0, accuracy=nan, sensitivity=nan, specificity=nan, misclassification_rate=nan, status=pending_manual_adjudication
- domain=SAE, n_reviewed=0, accuracy=nan, sensitivity=nan, specificity=nan, misclassification_rate=nan, status=pending_manual_adjudication


## External Face-Validity Checks
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, expected_direction=uncertain_or_small_benefit, observed_direction=not_estimated, concordance=not_evaluable
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, expected_direction=uncertain_or_small_benefit, observed_direction=not_estimated, concordance=not_evaluable
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, expected_direction=benefit, observed_direction=not_estimated, concordance=not_evaluable
- intervention_class=SGLT2 inhibitors, outcome=SAE, expected_direction=neutral_or_benefit, observed_direction=uncertain, concordance=full_concordance


## Reporting-Bias Framework Alignment
- intervention_class=ARB/ACEi, outcome=HF_HOSPITALIZATION, metric=ecr_participants, value=0.0, framework=SWiM, framework_item=Item 5/6 (synthesis grouping and data contribution)
- intervention_class=ARB/ACEi, outcome=HF_HOSPITALIZATION, metric=ecr_trials, value=0.0, framework=SWiM, framework_item=Item 5/6 (synthesis grouping and data contribution)
- intervention_class=ARB/ACEi, outcome=HF_HOSPITALIZATION, metric=eligible_completed_trials, value=8, framework=PRISMA 2020, framework_item=Item 16a (study selection)
- intervention_class=ARB/ACEi, outcome=HF_HOSPITALIZATION, metric=endpoint_alignment_rate, value=nan, framework=SWiM, framework_item=Item 7 (standardised metric and comparability)
- intervention_class=ARB/ACEi, outcome=HF_HOSPITALIZATION, metric=heterogeneity_i2, value=nan, framework=PRISMA 2020, framework_item=Item 20b/20d (results of syntheses, heterogeneity)
- intervention_class=ARB/ACEi, outcome=HF_HOSPITALIZATION, metric=reporting_debt_rate, value=0.25, framework=ROB-ME, framework_item=Risk due to missing results
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, metric=ecr_participants, value=0.0, framework=SWiM, framework_item=Item 5/6 (synthesis grouping and data contribution)
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, metric=ecr_trials, value=0.0, framework=SWiM, framework_item=Item 5/6 (synthesis grouping and data contribution)


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
