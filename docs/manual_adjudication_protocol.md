# Manual Adjudication Protocol (Gold Standard Validation)

## Goal
Quantify extraction accuracy and misclassification rates for registry outcome harmonization.

## Files
- Candidate pool: `outputs/validation_outcome_candidates.csv`
- Review template: `outputs/validation_adjudication_sample.csv`
- Scored metrics: `outputs/validation_metrics.csv`
- Misclassification log: `outputs/validation_misclassified.csv`

## Review Steps
1. Run the pipeline to generate the adjudication sample template.
2. Two independent reviewers label `consensus_include` for each sampled row:
   - `1` include
   - `0` exclude
3. Save completed consensus file as CSV.
4. Re-run pipeline with:
   - `--adjudication_path path/to/consensus.csv`
5. Review `validation_metrics.csv` and `validation_misclassified.csv`.

## Suggested Reporting in Manuscript
- Number of adjudicated records per domain.
- Accuracy, sensitivity, specificity, PPV, NPV.
- Misclassification rate and dominant error mode (FP vs FN).
- Examples of recurrent failure modes (e.g., composite endpoint ambiguity).
