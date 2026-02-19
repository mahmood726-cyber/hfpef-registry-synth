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


def test_hf_hosp_matcher_excludes_composite_and_hierarchical_outcomes():
    assert not is_hf_hosp_outcome("Occurrence of the composite endpoint of cardiovascular death and heart failure hospitalization")
    assert not is_hf_hosp_outcome("Hierarchical composite endpoint: percentage of wins of participant pairs")
    assert not is_hf_hosp_outcome("Participants with treatment emergent adverse events")
    assert not is_hf_hosp_outcome("Time to first event of adjudicated cardiovascular (CV) death or adjudicated hospitalisation for heart failure")
    assert not is_hf_hosp_outcome("(Single Arm) HFHs [Subject Based COVID-19 Sensitivity Analysis]")
    assert not is_hf_hosp_outcome("Number of subjects with first clinical worsening event from baseline to week 24")
    assert not is_hf_hosp_outcome("(Randomized Arm) All-cause Hospitalizations")
    assert not is_hf_hosp_outcome("Occurrence of adjudicated hospitalisation for heart failure (HHF) (First and Recurrent)")
    assert not is_hf_hosp_outcome("Time to first death or heart failure hospitalization")


def test_choose_preferred_outcome_longest_followup():
    outcomes = [
        {"title": "HF hospitalization", "description": "", "timeFrame": "6 months"},
        {"title": "Hospitalization for heart failure", "description": "", "timeFrame": "18 months"},
    ]
    choice = choose_preferred_outcome(outcomes, is_hf_hosp_outcome)
    assert choice is not None
    assert choice.time_months is not None
    assert choice.time_months > 12
