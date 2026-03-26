# Registry-First Transparency-Adjusted Evidence Synthesis for Heart Failure with Preserved Ejection Fraction: A Decision-Grade Framework

## Authors

Mahmood Ahmad^1

^1 Royal Free Hospital, London, United Kingdom

Correspondence: mahmood.ahmad2@nhs.net | ORCID: 0009-0003-7781-4478

---

## Abstract

**Background:** HFpEF remains a therapeutic challenge with heterogeneous trial evidence across drug classes (SGLT2 inhibitors, MRAs, ARNIs, ARBs, sGC stimulators). Current evidence synthesis treats published trials as the complete evidence base, ignoring the substantial reporting gap in registered trials.

**Methods:** We built a registry-first transparency-adjusted synthesis framework that defines the trial denominator from ClinicalTrials.gov registrations (2015-present), measures evidence coverage ratios (ECR), computes class-level pooled effects with missing-not-at-random (MNAR) sensitivity, and produces decision-grade absolute effects per 1,000 patients at configurable baseline risks.

**Results:** Of 410 eligible HFpEF interventional trials, 151 were completed and 72 had posted CT.gov results modules. For the SGLT2 inhibitor class (k=7 for SAE, k=1 for HF hospitalisation), the pooled RR for serious adverse events was 0.98 (95% CI 0.88-1.10, I-squared=37.4%), consistent with safety. Trust scores ranged from 25 (ARB/ACEi, lowest ECR) to 50 (SGLT2i, highest ECR). MNAR sensitivity analyses showed conclusions were robust to delta adjustments of +0.1 and +0.2 for the "Other" class HF hospitalisation outcome.

**Conclusions:** Registry-first synthesis reveals that the HFpEF evidence base is substantially incomplete (ECR_trials < 10% for most classes). Trust scores provide a quantitative measure of evidence completeness that should accompany any treatment recommendation. Decision-grade absolute effects enable direct comparison of net benefit across drug classes at clinically relevant baseline risks.

---

## 1. Introduction

Heart failure with preserved ejection fraction (HFpEF) accounts for approximately half of all heart failure diagnoses, yet therapeutic options remain limited compared with HFrEF. The EMPEROR-Preserved and DELIVER trials established SGLT2 inhibitors as the first drug class with consistent benefit in HFpEF, but the evidence landscape across other classes (MRAs, ARNIs, sGC stimulators) remains fragmented and incomplete.

Standard meta-analyses of HFpEF trials pool published results without accounting for the substantial number of completed trials that have not posted results or published findings. This reporting gap introduces systematic bias: trials with unfavourable results are less likely to be published, inflating apparent treatment benefits.

We developed a registry-first transparency-adjusted synthesis framework that inverts the standard approach: starting from the registered trial universe rather than published literature, explicitly measuring evidence coverage, and adjusting pooled estimates under missing-not-at-random assumptions.

## 2. Methods

### 2.1 Trial Universe

We queried ClinicalTrials.gov for all interventional HFpEF trials (Phase 2-4) with start dates from 2015 onwards. Trials were classified by intervention class using automated keyword matching: SGLT2 inhibitors, MRAs, ARNIs, ARBs, beta-blockers, sGC stimulators, neprilysin inhibitors, and Other.

### 2.2 Evidence Coverage Ratios

ECR_trials = published trials / completed trials. ECR_participants = published participant total / completed participant total. These measure how complete the evidence base is for each drug class.

### 2.3 Class-Level Synthesis

For each drug class with >= 1 extractable trial, we computed pooled risk ratios using DerSimonian-Laird random-effects models for two outcomes: HF hospitalisation and serious adverse events (SAE).

### 2.4 Trust Scores

A composite trust score (0-100) integrates: ECR_trials, ECR_participants, reporting debt rate (fraction of completed trials without results), and data quality indicators. Higher scores indicate more complete and transparent evidence.

### 2.5 Decision-Grade Absolute Effects

Pooled relative effects were converted to absolute risk differences per 1,000 patients at three baseline risks (50, 100, 200 per 1,000), enabling direct comparison of net clinical benefit across drug classes.

### 2.6 MNAR Sensitivity

Three scenarios for unreported trial results: S0 (missing at random), delta +0.10 (modest attenuation toward null), delta +0.20 (substantial attenuation).

## 3. Results

### 3.1 Trial Universe

410 eligible HFpEF trials were identified. 151 completed, 72 with posted results modules. Evidence coverage was lowest for ARB/ACEi (ECR_trials = 0%), moderate for SGLT2 inhibitors (ECR_trials = 7.1%, ECR_participants = 42.8%), and generally poor across most classes.

### 3.2 Pooled Effects

SGLT2 inhibitors showed favourable safety (SAE pooled RR = 0.98, 95% CI 0.88-1.10, I-squared = 37.4%, k=7). The "Other" class showed a large but imprecise reduction in HF hospitalisation (RR = 0.40, 95% CI 0.03-5.65, k=1). Most drug classes had insufficient data for meaningful pooled estimates.

### 3.3 Decision-Grade Outputs

At baseline risk of 100 per 1,000: the "Other" class showed an absolute risk reduction of 60 per 1,000 for HF hospitalisation (highly uncertain, single study). SGLT2 inhibitors showed negligible excess SAE risk (1.6 per 1,000).

### 3.4 Trust and Robustness

SGLT2 inhibitors had the highest trust score (50/100), reflecting their relatively better evidence coverage. ARB/ACEi had the lowest (25/100). MNAR sensitivity showed stability under delta +0.1 and +0.2 adjustments for the main findings.

## 4. Discussion

This registry-first synthesis reveals the uncomfortable truth about HFpEF evidence: despite 410 registered trials, evidence coverage is below 10% for most drug classes. The SGLT2 inhibitor class has the most complete evidence base but still has only 42.8% participant-weighted coverage.

Trust scores provide a novel quantitative complement to GRADE certainty ratings. While GRADE assesses the quality of available evidence, trust scores measure the completeness of evidence — whether we are seeing the full picture.

### Limitations

The framework depends on ClinicalTrials.gov registration completeness. Pre-2015 trials are excluded. Class-level grouping may mask within-class heterogeneity. Single-study pooled estimates for HF hospitalisation are unreliable.

## 5. Conclusions

Registry-first synthesis with transparency adjustment reveals that the HFpEF evidence base is substantially incomplete. Trust scores and MNAR sensitivity should accompany all treatment recommendations in this therapeutic area.

---

## Data Availability

Pipeline code and outputs at https://github.com/mahmood726-cyber/hfpef-registry-synth.

## Funding
None.

## Competing Interests
The author declares no competing interests.

## References
1. Anker SD, et al. Empagliflozin in heart failure with a preserved ejection fraction. NEJM. 2021;385:1451-1461.
2. Solomon SD, et al. Dapagliflozin in heart failure with mildly reduced or preserved ejection fraction. NEJM. 2022;387:1089-1098.
3. Pitt B, et al. Spironolactone for heart failure with preserved ejection fraction. NEJM. 2014;370:1383-1392.
4. DeVito NJ, et al. Compliance with legal requirement to report clinical trial results. Lancet. 2020;395:361-369.
