from hfpef_registry_synth.mapping import classify_comparator, classify_intervention


def test_intervention_class_mapping_sglt2():
    mapped = classify_intervention("Empagliflozin 10 mg")
    assert mapped.class_name == "SGLT2 inhibitors"


def test_intervention_class_mapping_arni():
    mapped = classify_intervention("Sacubitril/Valsartan")
    assert mapped.class_name == "ARNI"


def test_comparator_mapping():
    assert classify_comparator("Placebo") == "Placebo/SoC"
    assert classify_comparator("Standard of care") == "Placebo/SoC"
