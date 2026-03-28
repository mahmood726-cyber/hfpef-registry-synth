# HFpEF Registry-First Transparency-Adjusted Synthesis

Generated: 2026-02-19 09:47 UTC

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
- Eligible HFpEF interventional trials: 320
- Completed trials: 122
- Trials with posted CT.gov results module: 57

## HF Hospitalization Synthesis (Class-level)
- intervention_class=MRA, k_studies=1, pooled_rr=0.8427099011666432, ci_low_rr=0.7911830793797883, ci_high_rr=0.8975924738949056, i2=0.0
- intervention_class=Other, k_studies=5, pooled_rr=1.008289575376717, ci_low_rr=0.8899739498808255, ci_high_rr=1.1423344109673068, i2=72.12076378658412
- intervention_class=SGLT2 inhibitors, k_studies=2, pooled_rr=0.8388529194992276, ci_low_rr=0.754554385727303, ci_high_rr=0.9325692539367021, i2=0.0
- intervention_class=sGC stimulators, k_studies=1, pooled_rr=0.9082031249999999, ci_low_rr=0.43060139849184387, ci_high_rr=1.915537012068921, i2=0.0


## SAE Synthesis (Class-level)
- intervention_class=MRA, k_studies=1, pooled_rr=0.790909090909091, ci_low_rr=0.5997862705122902, ci_high_rr=1.0429334928729865, i2=0.0
- intervention_class=Other, k_studies=22, pooled_rr=0.9875510698080897, ci_low_rr=0.750144793922192, ci_high_rr=1.3000918267790578, i2=0.0
- intervention_class=SGLT2 inhibitors, k_studies=5, pooled_rr=0.7813519175761899, ci_low_rr=0.7246947806539485, ci_high_rr=0.8424385484728862, i2=45.993026193734735
- intervention_class=sGC stimulators, k_studies=3, pooled_rr=0.9362525751739763, ci_low_rr=0.479484213300699, ci_high_rr=1.8281496245428612, i2=0.0


## Decision-Grade Absolute Effects (per 1000)
- intervention_class=MRA, baseline_risk_per_1000=50, arr_hfhosp_per_1000=7.864504941667839, ari_sae_per_1000=-10.454545454545453, net_benefit_per_1000=18.319050396213292
- intervention_class=MRA, baseline_risk_per_1000=100, arr_hfhosp_per_1000=15.729009883335678, ari_sae_per_1000=-20.909090909090907, net_benefit_per_1000=36.638100792426584
- intervention_class=MRA, baseline_risk_per_1000=200, arr_hfhosp_per_1000=31.458019766671356, ari_sae_per_1000=-41.81818181818181, net_benefit_per_1000=73.27620158485317
- intervention_class=Other, baseline_risk_per_1000=50, arr_hfhosp_per_1000=-0.4144787688358491, ari_sae_per_1000=-0.6224465095955125, net_benefit_per_1000=0.2079677407596634
- intervention_class=Other, baseline_risk_per_1000=100, arr_hfhosp_per_1000=-0.8289575376716982, ari_sae_per_1000=-1.244893019191025, net_benefit_per_1000=0.4159354815193268
- intervention_class=Other, baseline_risk_per_1000=200, arr_hfhosp_per_1000=-1.6579150753433964, ari_sae_per_1000=-2.48978603838205, net_benefit_per_1000=0.8318709630386536
- intervention_class=SGLT2 inhibitors, baseline_risk_per_1000=50, arr_hfhosp_per_1000=8.05735402503862, ari_sae_per_1000=-10.932404121190501, net_benefit_per_1000=18.98975814622912
- intervention_class=SGLT2 inhibitors, baseline_risk_per_1000=100, arr_hfhosp_per_1000=16.11470805007724, ari_sae_per_1000=-21.864808242381002, net_benefit_per_1000=37.97951629245824


## Trust Capsules
- intervention_class=ARNI, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.16666666666666666, trust_score=25
- intervention_class=Beta blockers, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.0, trust_score=35
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, ecr_trials=1.0, ecr_participants=0.9975066489361702, reporting_debt_rate=0.0, trust_score=85
- intervention_class=Other, outcome=HF_HOSPITALIZATION, ecr_trials=0.049019607843137254, ecr_participants=0.1585838483293181, reporting_debt_rate=0.6235294117647059, trust_score=25
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, ecr_trials=0.2222222222222222, ecr_participants=0.8943641407504745, reporting_debt_rate=0.14285714285714285, trust_score=85
- intervention_class=Unknown, outcome=HF_HOSPITALIZATION, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.0, trust_score=35
- intervention_class=sGC stimulators, outcome=HF_HOSPITALIZATION, ecr_trials=0.3333333333333333, ecr_participants=0.34465317919075145, reporting_debt_rate=0.3333333333333333, trust_score=40
- intervention_class=ARNI, outcome=SAE, ecr_trials=0.0, ecr_participants=0.0, reporting_debt_rate=0.16666666666666666, trust_score=25


## MNAR Transparency-Adjusted Sensitivity
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, scenario=S0_MAR, observed_rr=0.8427099011666432, adjusted_rr=0.8427099011666432, conclusion_change=stable, robust_under_scenario=True
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, scenario=delta_+0.10, observed_rr=0.8427099011666432, adjusted_rr=0.8427099011666432, conclusion_change=stable, robust_under_scenario=True
- intervention_class=MRA, outcome=HF_HOSPITALIZATION, scenario=delta_+0.20, observed_rr=0.8427099011666432, adjusted_rr=0.8427099011666432, conclusion_change=stable, robust_under_scenario=True
- intervention_class=Other, outcome=HF_HOSPITALIZATION, scenario=S0_MAR, observed_rr=1.008289575376717, adjusted_rr=1.008289575376717, conclusion_change=stable, robust_under_scenario=True
- intervention_class=Other, outcome=HF_HOSPITALIZATION, scenario=delta_+0.10, observed_rr=1.008289575376717, adjusted_rr=1.097719647443607, conclusion_change=stable, robust_under_scenario=True
- intervention_class=Other, outcome=HF_HOSPITALIZATION, scenario=delta_+0.20, observed_rr=1.008289575376717, adjusted_rr=1.1950817045128226, conclusion_change=stable, robust_under_scenario=True
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, scenario=S0_MAR, observed_rr=0.8388529194992276, adjusted_rr=0.8388529194992276, conclusion_change=stable, robust_under_scenario=True
- intervention_class=SGLT2 inhibitors, outcome=HF_HOSPITALIZATION, scenario=delta_+0.10, observed_rr=0.8388529194992276, adjusted_rr=0.847761183158267, conclusion_change=stable, robust_under_scenario=True


## Interpretation Notes
- No SUCRA or ordinal ranking is produced.
- Decision support is expressed as absolute effects and net tradeoffs with uncertainty.
- Trust score is explicit and editable, not a black-box model.

## Known Limitations
- Registry outcomes may not align exactly with publication endpoint definitions.
- Missing PDFs and non-posted results remain partially unobserved by design.
- SAE tables can differ in whether they report subjects vs events; this is flagged in extracts.
