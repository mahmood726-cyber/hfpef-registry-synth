# HFpEF Registry-First Transparency-Adjusted Synthesis

Generated: 2026-02-19 17:23 UTC

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
- intervention_class=SGLT2 inhibitors, k_studies=1, pooled_rr=0.665331998665332, ci_low_rr=0.18794064186889392, ci_high_rr=2.355353605511289, i2=0.0


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
- intervention_class=ARB/ACEi, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.25, trust_score=25
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.14285714285714285, trust_score=35
- intervention_class=Beta blockers, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.0, trust_score=35
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.0, trust_score=35
- intervention_class=Neprilysin inhibitors, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.0, trust_score=35
- intervention_class=Other, outcome=HF_HOSPITALIZATION, ecr_trials=0.008, ecr_participants=0.0020285445193073967, reporting_debt_rate=0.5961538461538461, trust_score=40
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, ecr_trials=0.07142857142857142, ecr_participants=0.42780595841966135, reporting_debt_rate=0.2, trust_score=50
- intervention_class=Unknown, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.0, trust_score=35


## MNAR Transparency-Adjusted Sensitivity
- intervention_class=Other, outcome=HF_HOSPITALIZATION, scenario=S0_MAR, observed_rr=0.4, adjusted_rr=0.4, conclusion_change=stable, robust_under_scenario=True
- intervention_class=Other, outcome=HF_HOSPITALIZATION, scenario=delta_+0.10, observed_rr=0.4, adjusted_rr=0.4419690947488921, conclusion_change=stable, robust_under_scenario=True
- intervention_class=Other, outcome=HF_HOSPITALIZATION, scenario=delta_+0.20, observed_rr=0.4, adjusted_rr=0.48834170178288794, conclusion_change=stable, robust_under_scenario=True
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, scenario=S0_MAR, observed_rr=0.665331998665332, adjusted_rr=0.665331998665332, conclusion_change=stable, robust_under_scenario=True
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, scenario=delta_+0.10, observed_rr=0.665331998665332, adjusted_rr=0.7045121421667538, conclusion_change=stable, robust_under_scenario=True
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, scenario=delta_+0.20, observed_rr=0.665331998665332, adjusted_rr=0.7459995302436229, conclusion_change=stable, robust_under_scenario=True
- intervention_class=ARB/ACEi, outcome=SAE, scenario=S0_MAR, observed_rr=0.8122362869198313, adjusted_rr=0.8122362869198313, conclusion_change=stable, robust_under_scenario=True
- intervention_class=ARB/ACEi, outcome=SAE, scenario=delta_+0.10, observed_rr=0.8122362869198313, adjusted_rr=0.8932518812990693, conclusion_change=stable, robust_under_scenario=True


## Interpretation Notes
- No SUCRA or ordinal ranking is produced.
- Decision support is expressed as absolute effects and net tradeoffs with uncertainty.
- Trust score is explicit and editable, not a black-box model.

## Known Limitations
- Registry outcomes may not align exactly with publication endpoint definitions.
- Missing PDFs and non-posted results remain partially unobserved by design.
- SAE synthesis uses participant-level totals where available (total SAE rows or event-group serious totals); event-count-only SAE tables are flagged and excluded from pooled RR.
