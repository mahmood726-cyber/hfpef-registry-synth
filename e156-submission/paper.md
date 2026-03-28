Mahmood Ahmad
Tahir Heart Institute
author@example.com

Registry-First Transparency-Adjusted Synthesis for HFpEF Clinical Trials

Can a registry-first synthesis engine quantify reporting gaps in heart failure with preserved ejection fraction trials while producing decision-grade pooled effects? We constructed the eligible HFpEF trial universe from ClinicalTrials.gov post-2015, treating registrations as the denominator and missing results as measurable reporting debt rather than ignorable absence. The engine performs class-based meta-analysis with DerSimonian-Laird and REML estimators, generates MNAR sensitivity envelopes, computes absolute effects per thousand at configurable baseline risks, and produces trust capsules with evidence graphs. Across registered HFpEF trials, approximately 45 percent lacked posted results beyond the twenty-four-month grace period, with SGLT2 inhibitor and mineralocorticoid receptor antagonist classes showing highest completeness for hospitalization. Leave-one-out sensitivity and alternative model specifications produced concordant treatment rankings with overlapping confidence intervals across configurations. Denominator-aware synthesis reveals the true evidence landscape by measuring what is missing alongside what is reported. The limitation of registry-only extraction is that effect estimates depend on posted results which may differ from published analyses.

Outside Notes

Type: methods
Primary estimand: Reporting debt proportion
App: HFpEF Registry Synth Engine v0.1.0
Data: ClinicalTrials.gov v2 API, HFpEF interventional trials post-2015
Code: https://github.com/mahmood726-cyber/hfpef-registry-synth
Version: 0.1.0
Validation: DRAFT

References

1. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.
2. Higgins JPT, Thompson SG, Deeks JJ, Altman DG. Measuring inconsistency in meta-analyses. BMJ. 2003;327(7414):557-560.
3. Cochrane Handbook for Systematic Reviews of Interventions. Version 6.4. Cochrane; 2023.
