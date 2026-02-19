from hfpef_registry_synth.universe import build_trial_universe


def _base_study(nct_id: str, brief_title: str, conditions: list[str], keywords: list[str], eligibility: str):
    return {
        "protocolSection": {
            "identificationModule": {
                "nctId": nct_id,
                "briefTitle": brief_title,
            },
            "statusModule": {
                "overallStatus": "COMPLETED",
                "primaryCompletionDateStruct": {"date": "2020-01-01"},
                "completionDateStruct": {"date": "2020-02-01"},
            },
            "designModule": {
                "studyType": "INTERVENTIONAL",
                "designInfo": {"allocation": "RANDOMIZED"},
                "enrollmentInfo": {"count": "120", "type": "ACTUAL"},
            },
            "conditionsModule": {
                "conditions": conditions,
                "keywords": keywords,
            },
            "eligibilityModule": {
                "eligibilityCriteria": eligibility,
            },
            "armsInterventionsModule": {
                "armGroups": [],
                "interventions": [],
            },
        }
    }


def test_hfpef_candidate_requires_heart_failure_context_or_explicit_hfpef():
    explicit_hfpef = _base_study(
        nct_id="NCT_HFPEF_1",
        brief_title="Drug X in HFpEF",
        conditions=["HFpEF"],
        keywords=["preserved ejection fraction"],
        eligibility="LVEF >= 50%",
    )
    preserved_ef_non_hf = _base_study(
        nct_id="NCT_NON_HF_1",
        brief_title="Preserved ejection fraction in aortic stenosis",
        conditions=["Aortic stenosis"],
        keywords=["preserved ejection fraction"],
        eligibility="LVEF >= 50%",
    )

    out = build_trial_universe([explicit_hfpef, preserved_ef_non_hf], start_year=2015).df

    assert set(out["nct_id"]) == {"NCT_HFPEF_1"}


def test_results_posted_uses_has_results_flag_when_results_section_absent():
    study = _base_study(
        nct_id="NCT_HAS_RESULTS",
        brief_title="HFpEF trial with hasResults flag",
        conditions=["Heart Failure with Preserved Ejection Fraction"],
        keywords=["HFpEF"],
        eligibility="LVEF >= 50%",
    )
    study["hasResults"] = True

    out = build_trial_universe([study], start_year=2015).df
    assert len(out) == 1
    assert bool(out.iloc[0]["results_posted"]) is True
