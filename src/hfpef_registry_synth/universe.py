"""Trial-universe construction from CT.gov protocol/registration modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd

from .mapping import classify_comparator, classify_intervention, normalize_drug_label
from .parsing import extract_ef_cutoff
from .utils import extract_date_from_struct, normalize_ws, safe_int, to_json_text, unique_preserve_order


EXPLICIT_HFPEF_TERMS = [
    "hfpef",
    "heart failure with preserved ejection fraction",
    "diastolic heart failure",
]

HF_CONTEXT_TERMS = [
    "heart failure",
    "congestive heart failure",
    "cardiac failure",
]

PRESERVED_EF_TERMS = [
    "preserved ejection fraction",
    "preserved ef",
    "normal ejection fraction",
]

HF_RELEVANT_EF_OPERATORS = {
    ">=",
    "=>",
    "at least",
    "greater than",
    "greater than or equal to",
    ">",
    "=",
}


@dataclass
class TrialUniverseResult:
    df: pd.DataFrame
    study_index: Dict[str, Dict[str, Any]]


def _protocol(study: Dict[str, Any]) -> Dict[str, Any]:
    return study.get("protocolSection", {})


def _results(study: Dict[str, Any]) -> Dict[str, Any]:
    return study.get("resultsSection", {})


def _id_module(study: Dict[str, Any]) -> Dict[str, Any]:
    return _protocol(study).get("identificationModule", {})


def _status_module(study: Dict[str, Any]) -> Dict[str, Any]:
    return _protocol(study).get("statusModule", {})


def _design_module(study: Dict[str, Any]) -> Dict[str, Any]:
    return _protocol(study).get("designModule", {})


def _conditions_module(study: Dict[str, Any]) -> Dict[str, Any]:
    return _protocol(study).get("conditionsModule", {})


def _arms_module(study: Dict[str, Any]) -> Dict[str, Any]:
    return _protocol(study).get("armsInterventionsModule", {})


def _outcomes_module(study: Dict[str, Any]) -> Dict[str, Any]:
    return _protocol(study).get("outcomesModule", {})


def _eligibility_module(study: Dict[str, Any]) -> Dict[str, Any]:
    return _protocol(study).get("eligibilityModule", {})


def _sponsors_module(study: Dict[str, Any]) -> Dict[str, Any]:
    return _protocol(study).get("sponsorCollaboratorsModule", {})


def _nct_id(study: Dict[str, Any]) -> str:
    return _id_module(study).get("nctId", "").upper()


def _is_interventional(study: Dict[str, Any]) -> bool:
    return _design_module(study).get("studyType", "").upper() == "INTERVENTIONAL"


def _is_rct_like(study: Dict[str, Any]) -> bool:
    design = _design_module(study)
    allocation = normalize_ws(design.get("designInfo", {}).get("allocation", "")).lower()
    if "random" in allocation:
        return True
    text_blobs = [
        _id_module(study).get("briefTitle", ""),
        _id_module(study).get("officialTitle", ""),
        normalize_ws(study.get("descriptionSection", {}).get("briefSummary", "")),
    ]
    merged = " ".join(text_blobs).lower()
    return "randomized" in merged or "randomised" in merged


def _primary_completion_year(study: Dict[str, Any]) -> Optional[int]:
    status = _status_module(study)
    dt = extract_date_from_struct(status.get("primaryCompletionDateStruct", {}))
    if dt:
        return dt.year
    dt = extract_date_from_struct(status.get("completionDateStruct", {}))
    return dt.year if dt else None


def _is_hfpef_candidate(study: Dict[str, Any]) -> bool:
    cond = _conditions_module(study)
    terms: List[str] = []
    terms.extend(cond.get("conditions", []) or [])
    terms.extend(cond.get("keywords", []) or [])
    terms.append(_id_module(study).get("briefTitle", ""))
    terms.append(_id_module(study).get("officialTitle", ""))
    eligibility = _eligibility_module(study).get("eligibilityCriteria", "")
    if eligibility:
        terms.append(str(eligibility))

    merged = " | ".join(t for t in terms if t)
    raw = normalize_ws(merged).lower()

    if any(term in raw for term in EXPLICIT_HFPEF_TERMS):
        return True

    has_hf_context = any(term in raw for term in HF_CONTEXT_TERMS)
    has_preserved_terms = any(term in raw for term in PRESERVED_EF_TERMS)
    if has_hf_context and has_preserved_terms:
        return True

    ef = extract_ef_cutoff([eligibility, merged])
    op = normalize_ws(ef.operator).lower()
    has_hf_relevant_ef = (
        ef.value is not None
        and ef.value >= 40
        and op in HF_RELEVANT_EF_OPERATORS
    )
    return has_hf_context and has_hf_relevant_ef


def _extract_outcomes(study: Dict[str, Any]) -> List[Dict[str, str]]:
    module = _outcomes_module(study)
    out: List[Dict[str, str]] = []
    for kind, key in (("PRIMARY", "primaryOutcomes"), ("SECONDARY", "secondaryOutcomes"), ("OTHER", "otherOutcomes")):
        for item in module.get(key, []) or []:
            out.append(
                {
                    "type": kind,
                    "title": normalize_ws(item.get("measure", "") or item.get("title", "")),
                    "description": normalize_ws(item.get("description", "")),
                    "timeFrame": normalize_ws(item.get("timeFrame", "")),
                }
            )
    return out


def _extract_arms_and_interventions(study: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    module = _arms_module(study)
    arms = module.get("armGroups", []) or []
    interventions = module.get("interventions", []) or []
    return arms, interventions


def _extract_enrollment(study: Dict[str, Any]) -> Tuple[Optional[int], str]:
    enrollment_info = _design_module(study).get("enrollmentInfo", {})
    enrollment = safe_int(enrollment_info.get("count"))
    enrollment_type = normalize_ws(enrollment_info.get("type", "")) or "UNKNOWN"
    return enrollment, enrollment_type


def _extract_dates(study: Dict[str, Any]) -> Dict[str, str]:
    status = _status_module(study)
    fields = {
        "start_date": status.get("startDateStruct", {}),
        "primary_completion_date": status.get("primaryCompletionDateStruct", {}),
        "completion_date": status.get("completionDateStruct", {}),
    }
    out: Dict[str, str] = {}
    for key, struct in fields.items():
        dt = extract_date_from_struct(struct)
        out[key] = dt.date().isoformat() if dt else ""
    return out


def _extract_intervention_classes(interventions: List[Dict[str, Any]], arms: List[Dict[str, Any]]) -> Tuple[List[str], List[str], str, str]:
    intervention_classes: List[str] = []
    comparator_classes: List[str] = []
    intervention_labels: List[str] = []

    for intervention in interventions:
        name = normalize_ws(intervention.get("name", ""))
        i_type = normalize_ws(intervention.get("type", ""))
        if not name:
            continue
        mapped = classify_intervention(name, i_type)
        intervention_labels.append(normalize_drug_label(name))
        if mapped.class_name == "Placebo/SoC":
            comparator_classes.append(mapped.class_name)
        else:
            intervention_classes.append(mapped.class_name)

    for arm in arms:
        label = normalize_ws(arm.get("label", "") or arm.get("armGroupLabel", ""))
        if not label:
            continue
        c = classify_comparator(label, None)
        if c == "Placebo/SoC":
            comparator_classes.append(c)

    intervention_classes = unique_preserve_order(intervention_classes)
    comparator_classes = unique_preserve_order(comparator_classes)
    primary_intervention = intervention_classes[0] if intervention_classes else "Unknown"
    primary_comparator = comparator_classes[0] if comparator_classes else "Unknown"
    return intervention_classes, comparator_classes, primary_intervention, primary_comparator


def _extract_sponsor_fields(study: Dict[str, Any]) -> Tuple[str, List[str]]:
    sponsors = _sponsors_module(study)
    lead = sponsors.get("leadSponsor", {}).get("name", "")
    collaborators = [c.get("name", "") for c in sponsors.get("collaborators", []) or [] if c.get("name")]
    return normalize_ws(lead), [normalize_ws(x) for x in collaborators]


def build_trial_universe(studies: Iterable[Dict[str, Any]], start_year: int = 2015) -> TrialUniverseResult:
    rows: List[Dict[str, Any]] = []
    study_index: Dict[str, Dict[str, Any]] = {}

    for study in studies:
        nct_id = _nct_id(study)
        if not nct_id:
            continue
        if not _is_interventional(study):
            continue
        if not _is_hfpef_candidate(study):
            continue
        rct_like = _is_rct_like(study)
        if not rct_like:
            continue

        pcy = _primary_completion_year(study)
        if pcy is not None and pcy < start_year:
            continue

        outcomes = _extract_outcomes(study)
        arms, interventions = _extract_arms_and_interventions(study)
        enrollment, enrollment_type = _extract_enrollment(study)
        dates = _extract_dates(study)
        sponsor, collaborators = _extract_sponsor_fields(study)

        ef_texts = [
            _eligibility_module(study).get("eligibilityCriteria", ""),
            " ".join((o.get("title", "") + " " + o.get("description", "")).strip() for o in outcomes),
        ]
        ef = extract_ef_cutoff(ef_texts)

        intervention_classes, comparator_classes, primary_intervention_class, primary_comparator_class = _extract_intervention_classes(
            interventions, arms
        )

        status = _status_module(study)
        row = {
            "nct_id": nct_id,
            "brief_title": normalize_ws(_id_module(study).get("briefTitle", "")),
            "official_title": normalize_ws(_id_module(study).get("officialTitle", "")),
            "overall_status": normalize_ws(status.get("overallStatus", "")),
            "start_date": dates["start_date"],
            "primary_completion_date": dates["primary_completion_date"],
            "completion_date": dates["completion_date"],
            "primary_completion_year": pcy,
            "enrollment": enrollment,
            "enrollment_type": enrollment_type,
            "lead_sponsor": sponsor,
            "collaborators": to_json_text(collaborators),
            "conditions": to_json_text(_conditions_module(study).get("conditions", []) or []),
            "keywords": to_json_text(_conditions_module(study).get("keywords", []) or []),
            "interventions": to_json_text(interventions),
            "arm_groups": to_json_text(arms),
            "outcomes": to_json_text(outcomes),
            "eligibility_criteria": _eligibility_module(study).get("eligibilityCriteria", ""),
            "ef_cutoff_operator": ef.operator,
            "ef_cutoff_value": ef.value,
            "ef_band": ef.band,
            "intervention_classes": to_json_text(intervention_classes),
            "comparator_classes": to_json_text(comparator_classes),
            "primary_intervention_class": primary_intervention_class,
            "primary_comparator_class": primary_comparator_class,
            "rct_likely": rct_like,
            "results_posted": bool(_results(study)) or bool(study.get("hasResults")),
            "ctgov_url": f"https://clinicaltrials.gov/study/{nct_id}",
        }
        rows.append(row)
        study_index[nct_id] = study

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["primary_completion_year", "nct_id"], na_position="last").reset_index(drop=True)

    return TrialUniverseResult(df=df, study_index=study_index)
