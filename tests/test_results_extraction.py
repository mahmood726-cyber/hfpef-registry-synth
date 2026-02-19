from hfpef_registry_synth.results_extraction import _extract_sae_rows


def _study_with_sae_module(serious_events, serious_totals_by_group=None):
    serious_totals_by_group = serious_totals_by_group or {}
    return {
        "protocolSection": {
            "identificationModule": {"nctId": "NCT_SAE_TEST"},
            "armsInterventionsModule": {
                "armGroups": [
                    {"id": "T1", "label": "Empagliflozin"},
                    {"id": "C1", "label": "Placebo"},
                ]
            },
        },
        "resultsSection": {
            "adverseEventsModule": {
                "timeFrame": "12 months",
                "eventGroups": [
                    {
                        "id": "T1",
                        "title": "Empagliflozin",
                        "subjectsAtRisk": "100",
                        **({"seriousNumAffected": serious_totals_by_group["T1"]} if "T1" in serious_totals_by_group else {}),
                    },
                    {
                        "id": "C1",
                        "title": "Placebo",
                        "subjectsAtRisk": "100",
                        **({"seriousNumAffected": serious_totals_by_group["C1"]} if "C1" in serious_totals_by_group else {}),
                    },
                ],
                "seriousEvents": serious_events,
            }
        },
    }


def _trial_meta():
    return {
        "primary_intervention_class": "SGLT2 inhibitors",
        "primary_comparator_class": "Placebo/SoC",
    }


def test_extract_sae_rows_inherits_parent_total_term_for_stats_children():
    study = _study_with_sae_module(
        serious_events=[
            {
                "term": "Total SAE",
                "stats": [
                    {"groupId": "T1", "subjectsAffected": "8"},
                    {"groupId": "C1", "subjectsAffected": "10"},
                ],
            }
        ]
    )

    rows = _extract_sae_rows(study, _trial_meta())
    assert len(rows) == 2

    by_group = {row["group_id"]: row for row in rows}
    assert by_group["T1"]["subjects_with_sae"] == 8
    assert by_group["C1"]["subjects_with_sae"] == 10
    assert by_group["T1"]["count_type"] == "subjects_with_>=1_sae"
    assert by_group["C1"]["count_type"] == "subjects_with_>=1_sae"
    assert by_group["T1"]["subjects_source"] == "term_total"
    assert by_group["C1"]["subjects_source"] == "term_total"
    assert by_group["T1"]["is_total_term_available"] is True
    assert by_group["C1"]["is_total_term_available"] is True
    assert by_group["T1"]["is_incomplete"] is False
    assert by_group["C1"]["is_incomplete"] is False


def test_extract_sae_rows_does_not_promote_non_total_subject_counts():
    study = _study_with_sae_module(
        serious_events=[
            {
                "term": "Cardiac disorders",
                "stats": [
                    {"groupId": "T1", "subjectsAffected": "6"},
                    {"groupId": "C1", "subjectsAffected": "7"},
                ],
            }
        ]
    )

    rows = _extract_sae_rows(study, _trial_meta())
    assert len(rows) == 2
    for row in rows:
        assert row["subjects_with_sae"] is None
        assert row["event_count"] is None
        assert row["count_type"] == "subjects_non_total_not_used"
        assert row["subjects_source"] == ""
        assert row["is_total_term_available"] is False
        assert row["is_incomplete"] is True


def test_extract_sae_rows_keeps_total_event_counts_flagged_incomplete_when_subjects_missing():
    study = _study_with_sae_module(
        serious_events=[
            {
                "term": "Total",
                "stats": [
                    {"groupId": "T1", "numEvents": "15"},
                    {"groupId": "C1", "numEvents": "12"},
                ],
            }
        ]
    )

    rows = _extract_sae_rows(study, _trial_meta())
    assert len(rows) == 2
    by_group = {row["group_id"]: row for row in rows}

    assert by_group["T1"]["subjects_with_sae"] is None
    assert by_group["C1"]["subjects_with_sae"] is None
    assert by_group["T1"]["event_count"] == 15
    assert by_group["C1"]["event_count"] == 12
    assert by_group["T1"]["count_type"] == "event_counts_total_only"
    assert by_group["C1"]["count_type"] == "event_counts_total_only"
    assert by_group["T1"]["subjects_source"] == ""
    assert by_group["C1"]["subjects_source"] == ""
    assert by_group["T1"]["is_total_term_available"] is True
    assert by_group["C1"]["is_total_term_available"] is True
    assert by_group["T1"]["is_incomplete"] is True
    assert by_group["C1"]["is_incomplete"] is True


def test_extract_sae_rows_uses_event_group_serious_totals_when_term_totals_absent():
    study = _study_with_sae_module(
        serious_events=[
            {
                "term": "Cardiac disorders",
                "stats": [
                    {"groupId": "T1", "numAffected": "6"},
                    {"groupId": "C1", "numAffected": "7"},
                ],
            }
        ],
        serious_totals_by_group={"T1": "11", "C1": "13"},
    )

    rows = _extract_sae_rows(study, _trial_meta())
    assert len(rows) == 2
    by_group = {row["group_id"]: row for row in rows}

    assert by_group["T1"]["subjects_with_sae"] == 11
    assert by_group["C1"]["subjects_with_sae"] == 13
    assert by_group["T1"]["count_type"] == "subjects_with_>=1_sae"
    assert by_group["C1"]["count_type"] == "subjects_with_>=1_sae"
    assert by_group["T1"]["subjects_source"] == "event_group_total"
    assert by_group["C1"]["subjects_source"] == "event_group_total"
    assert by_group["T1"]["is_total_term_available"] is False
    assert by_group["C1"]["is_total_term_available"] is False
    assert by_group["T1"]["is_incomplete"] is False
    assert by_group["C1"]["is_incomplete"] is False
