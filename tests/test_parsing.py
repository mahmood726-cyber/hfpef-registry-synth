from hfpef_registry_synth.parsing import (
    choose_preferred_outcome,
    extract_ef_cutoff,
    is_hf_hosp_outcome,
    is_sae_outcome,
)


def test_extract_ef_cutoff_strict():
    result = extract_ef_cutoff(["Eligibility: LVEF >= 50% required."])
    assert result.value == 50
    assert result.band == "strict_hfpef"


def test_extract_ef_cutoff_mixed():
    result = extract_ef_cutoff(["Ejection fraction >= 40% allowed."])
    assert result.value == 40
    assert result.band == "mixed_or_midrange"


def test_outcome_matchers():
    assert is_hf_hosp_outcome("Time to first hospitalization for heart failure")
    assert is_sae_outcome("Participants with serious adverse events")


def test_choose_preferred_outcome_longest_followup():
    outcomes = [
        {"title": "HF hospitalization", "description": "", "timeFrame": "6 months"},
        {"title": "Hospitalization for heart failure", "description": "", "timeFrame": "18 months"},
    ]
    choice = choose_preferred_outcome(outcomes, is_hf_hosp_outcome)
    assert choice is not None
    assert choice.time_months is not None
    assert choice.time_months > 12
