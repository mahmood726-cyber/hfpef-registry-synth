"""Extraction of HF hospitalization and SAE arm-level results from CT.gov results modules."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd

from .ctgov_client import ctgov_record_url
from .mapping import classify_comparator, classify_intervention
from .parsing import choose_preferred_outcome, is_hf_hosp_outcome, is_sae_outcome, parse_timeframe_months
from .utils import normalize_ws, safe_float, safe_int


@dataclass
class ExtractionResult:
    hfhosp_df: pd.DataFrame
    sae_df: pd.DataFrame


def _nct_id(study: Dict[str, Any]) -> str:
    return (
        study.get("protocolSection", {})
        .get("identificationModule", {})
        .get("nctId", "")
        .upper()
    )


def _results(study: Dict[str, Any]) -> Dict[str, Any]:
    return study.get("resultsSection", {}) or {}


def _outcome_measures(study: Dict[str, Any]) -> List[Dict[str, Any]]:
    return _results(study).get("outcomeMeasuresModule", {}).get("outcomeMeasures", []) or []


def _arm_group_candidates(study: Dict[str, Any]) -> List[Dict[str, Any]]:
    return (
        study.get("protocolSection", {})
        .get("armsInterventionsModule", {})
        .get("armGroups", [])
        or []
    )


def _group_map_from_outcome(outcome: Dict[str, Any]) -> Dict[str, str]:
    group_map: Dict[str, str] = {}
    for group in outcome.get("groups", []) or []:
        gid = str(group.get("id") or group.get("groupId") or "").strip()
        title = normalize_ws(group.get("title", "") or group.get("groupTitle", ""))
        if gid:
            group_map[gid] = title or gid
    return group_map


def _fallback_group_map(study: Dict[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for idx, arm in enumerate(_arm_group_candidates(study), start=1):
        label = normalize_ws(arm.get("label", "") or arm.get("armGroupLabel", ""))
        gid = str(arm.get("id") or arm.get("armGroupId") or f"ARM{idx}")
        out[gid] = label or gid
    return out


def _extract_denoms(outcome: Dict[str, Any]) -> Dict[str, int]:
    denoms: Dict[str, int] = {}
    for denom in outcome.get("denoms", []) or []:
        for count in denom.get("counts", []) or []:
            gid = str(count.get("groupId") or count.get("id") or "").strip()
            value = safe_int(count.get("value"))
            if gid and value is not None:
                denoms[gid] = max(value, denoms.get(gid, 0))
    return denoms


def _extract_measurements(outcome: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Extract one best measurement per group for binary-event style outcomes."""
    candidates: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for cls in outcome.get("classes", []) or []:
        class_title = normalize_ws(cls.get("title", ""))
        for cat in cls.get("categories", []) or []:
            category_title = normalize_ws(cat.get("title", ""))
            for meas in cat.get("measurements", []) or []:
                gid = str(meas.get("groupId") or meas.get("id") or "").strip()
                value = safe_float(meas.get("value"))
                if not gid or value is None:
                    continue
                candidates[gid].append(
                    {
                        "value": value,
                        "class_title": class_title,
                        "category_title": category_title,
                        "spread": normalize_ws(str(meas.get("spread", ""))),
                    }
                )

    out: Dict[str, Dict[str, Any]] = {}
    for gid, rows in candidates.items():
        # Prefer categories that look like totals and integer-like values.
        rows_sorted = sorted(
            rows,
            key=lambda r: (
                0 if "total" in (r["category_title"] + " " + r["class_title"]).lower() else 1,
                0 if abs(r["value"] - round(r["value"])) < 1e-6 else 1,
                -r["value"],
            ),
        )
        best = rows_sorted[0]
        out[gid] = best
    return out


def _classify_arm(
    group_name: str,
    primary_intervention_class: str,
    primary_comparator_class: str,
) -> Tuple[str, str, str]:
    comp = classify_comparator(group_name)
    if comp == "Placebo/SoC":
        return "comparator", "Placebo/SoC", "placebo"

    mapped = classify_intervention(group_name)
    arm_class = mapped.class_name
    if arm_class in {"Unknown", "Other"}:
        arm_class = primary_intervention_class if primary_intervention_class != "Unknown" else arm_class
    role = "treatment"
    if arm_class == primary_comparator_class == "Placebo/SoC":
        role = "comparator"
    return role, arm_class, mapped.canonical_term or ""


def _extract_hfhosp_rows_for_outcome(
    study: Dict[str, Any],
    outcome: Dict[str, Any],
    trial_meta: Dict[str, Any],
    outcome_idx: int,
) -> List[Dict[str, Any]]:
    nct_id = _nct_id(study)
    group_map = _group_map_from_outcome(outcome)
    if not group_map:
        group_map = _fallback_group_map(study)
    denoms = _extract_denoms(outcome)
    measures = _extract_measurements(outcome)

    rows: List[Dict[str, Any]] = []
    timeframe = normalize_ws(outcome.get("timeFrame", ""))
    time_months = parse_timeframe_months(timeframe)
    title = normalize_ws(outcome.get("title", ""))
    description = normalize_ws(outcome.get("description", ""))

    for gid, gname in group_map.items():
        meas = measures.get(gid, {})
        value = safe_float(meas.get("value"))
        denom = denoms.get(gid)
        events = safe_int(value) if value is not None else None
        is_event_count = bool(
            events is not None and denom is not None and 0 <= events <= denom
        )
        is_rate_only = value is not None and (denom is None or not is_event_count)

        role, arm_class, arm_label = _classify_arm(
            gname,
            trial_meta.get("primary_intervention_class", "Unknown"),
            trial_meta.get("primary_comparator_class", "Unknown"),
        )

        rows.append(
            {
                "nct_id": nct_id,
                "outcome_domain": "HF_HOSPITALIZATION",
                "outcome_title": title,
                "outcome_description": description,
                "time_frame": timeframe,
                "time_months": time_months,
                "outcome_idx": outcome_idx,
                "module_path": f"resultsSection.outcomeMeasuresModule.outcomeMeasures[{outcome_idx}]",
                "group_id": gid,
                "arm_group_name": gname,
                "arm_role": role,
                "arm_class": arm_class,
                "arm_label": arm_label,
                "events": events if is_event_count else None,
                "denominator": denom,
                "value_raw": value,
                "is_event_count": is_event_count,
                "is_rate_only": is_rate_only,
                "incomplete_reason": "missing_denominator_or_noncount" if is_rate_only else "",
                "source_url": ctgov_record_url(nct_id),
            }
        )
    return rows


def _extract_hfhosp_rows(study: Dict[str, Any], trial_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    outcomes = _outcome_measures(study)
    brief = [
        {
            "title": normalize_ws(o.get("title", "")),
            "description": normalize_ws(o.get("description", "")),
            "timeFrame": normalize_ws(o.get("timeFrame", "")),
        }
        for o in outcomes
    ]
    choice = choose_preferred_outcome(brief, is_hf_hosp_outcome)
    if choice is None:
        return []

    idx = choice.source_idx
    return _extract_hfhosp_rows_for_outcome(study, outcomes[idx], trial_meta, idx)


def _extract_event_group_map(module: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, int]]:
    group_map: Dict[str, str] = {}
    group_n: Dict[str, int] = {}

    for group in module.get("eventGroups", []) or module.get("groups", []) or []:
        gid = str(group.get("id") or group.get("groupId") or "").strip()
        title = normalize_ws(group.get("title", "") or group.get("groupTitle", ""))
        if gid:
            group_map[gid] = title or gid
            den = safe_int(
                group.get("subjectsAtRisk")
                or group.get("numAtRisk")
                or group.get("denominator")
                or group.get("numParticipants")
            )
            if den is not None:
                group_n[gid] = den
    return group_map, group_n


def _collect_serious_records(node: Any, path: str = "") -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if isinstance(node, dict):
        gid = node.get("groupId") or node.get("id")
        affected = safe_int(
            node.get("subjectsAffected")
            or node.get("numAffected")
            or node.get("subjectsWithEvents")
            or node.get("numSubjectsAffected")
        )
        events = safe_int(node.get("numEvents") or node.get("events"))
        denom = safe_int(
            node.get("subjectsAtRisk")
            or node.get("numAtRisk")
            or node.get("denominator")
            or node.get("numParticipants")
        )
        term = normalize_ws(
            str(
                node.get("term")
                or node.get("event")
                or node.get("title")
                or node.get("adverseEventTerm")
                or ""
            )
        )

        if gid and (affected is not None or events is not None):
            out.append(
                {
                    "group_id": str(gid),
                    "subjects_affected": affected,
                    "events": events,
                    "denominator": denom,
                    "term": term,
                    "path": path,
                }
            )

        for k, v in node.items():
            out.extend(_collect_serious_records(v, f"{path}.{k}" if path else k))

    elif isinstance(node, list):
        for idx, item in enumerate(node):
            out.extend(_collect_serious_records(item, f"{path}[{idx}]"))

    return out


def _extract_sae_rows(study: Dict[str, Any], trial_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    nct_id = _nct_id(study)
    module = _results(study).get("adverseEventsModule", {})
    if not module:
        return []

    group_map, group_n = _extract_event_group_map(module)
    if not group_map:
        group_map = _fallback_group_map(study)

    serious_nodes = module.get("seriousEvents") if isinstance(module, dict) else None
    records = _collect_serious_records(serious_nodes if serious_nodes is not None else module, "resultsSection.adverseEventsModule")
    if not records:
        return []

    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in records:
        grouped[rec["group_id"]].append(rec)

    rows: List[Dict[str, Any]] = []
    for gid, recs in grouped.items():
        gname = group_map.get(gid, gid)
        totals = [r for r in recs if "total" in (r.get("term", "").lower())]

        subjects = None
        count_type = "subjects_with_>=1_sae"
        if totals:
            subjects = max((r.get("subjects_affected") for r in totals if r.get("subjects_affected") is not None), default=None)
        if subjects is None:
            subjects = max((r.get("subjects_affected") for r in recs if r.get("subjects_affected") is not None), default=None)
            if subjects is not None:
                count_type = "subjects_from_max_term"

        events = None
        if subjects is None:
            events = sum(r.get("events") or 0 for r in recs)
            count_type = "event_counts_only"

        denom = group_n.get(gid)
        if denom is None:
            denom = max((r.get("denominator") for r in recs if r.get("denominator") is not None), default=None)

        role, arm_class, arm_label = _classify_arm(
            gname,
            trial_meta.get("primary_intervention_class", "Unknown"),
            trial_meta.get("primary_comparator_class", "Unknown"),
        )

        rows.append(
            {
                "nct_id": nct_id,
                "outcome_domain": "SAE",
                "time_frame": normalize_ws(module.get("timeFrame", "")),
                "time_months": parse_timeframe_months(normalize_ws(module.get("timeFrame", ""))),
                "module_path": "resultsSection.adverseEventsModule",
                "group_id": gid,
                "arm_group_name": gname,
                "arm_role": role,
                "arm_class": arm_class,
                "arm_label": arm_label,
                "subjects_with_sae": subjects,
                "event_count": events,
                "denominator": denom,
                "count_type": count_type,
                "is_event_count": subjects is not None and denom is not None and subjects <= denom,
                "is_incomplete": subjects is None and events is not None,
                "source_url": ctgov_record_url(nct_id),
            }
        )
    return rows


def extract_results(
    studies: Dict[str, Dict[str, Any]],
    trial_meta_map: Dict[str, Dict[str, Any]],
) -> ExtractionResult:
    hfhosp_rows: List[Dict[str, Any]] = []
    sae_rows: List[Dict[str, Any]] = []

    for nct_id, study in studies.items():
        trial_meta = trial_meta_map.get(nct_id, {})
        if not _results(study):
            continue

        hfhosp_rows.extend(_extract_hfhosp_rows(study, trial_meta))
        sae_rows.extend(_extract_sae_rows(study, trial_meta))

    hfhosp_df = pd.DataFrame(hfhosp_rows)
    sae_df = pd.DataFrame(sae_rows)

    if not hfhosp_df.empty:
        hfhosp_df = hfhosp_df.sort_values(["nct_id", "outcome_idx", "arm_group_name"]).reset_index(drop=True)
    if not sae_df.empty:
        sae_df = sae_df.sort_values(["nct_id", "arm_group_name"]).reset_index(drop=True)

    return ExtractionResult(hfhosp_df=hfhosp_df, sae_df=sae_df)
