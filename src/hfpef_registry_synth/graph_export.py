"""Evidence graph edge/node export utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List

import pandas as pd

from .utils import normalize_ws


@dataclass
class GraphTables:
    edges: pd.DataFrame
    trial_nodes: pd.DataFrame
    class_nodes: pd.DataFrame


def _json_list(text: Any) -> List[Any]:
    if text is None:
        return []
    if isinstance(text, list):
        return text
    if isinstance(text, str):
        text = text.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return []
    return []


def build_evidence_graph(universe_df: pd.DataFrame, hfhosp_df: pd.DataFrame, sae_df: pd.DataFrame) -> GraphTables:
    edges: List[Dict[str, Any]] = []

    for _, row in universe_df.iterrows():
        nct_id = row["nct_id"]

        for cls in _json_list(row.get("intervention_classes")):
            cls = normalize_ws(str(cls))
            if not cls:
                continue
            edges.append(
                {
                    "node_type_from": "trial",
                    "node_id_from": nct_id,
                    "edge_type": "TESTS",
                    "node_type_to": "intervention_class",
                    "node_id_to": cls,
                    "attributes": json.dumps({}),
                }
            )

        for cls in _json_list(row.get("comparator_classes")):
            cls = normalize_ws(str(cls))
            if not cls:
                continue
            edges.append(
                {
                    "node_type_from": "trial",
                    "node_id_from": nct_id,
                    "edge_type": "COMPARES",
                    "node_type_to": "comparator_class",
                    "node_id_to": cls,
                    "attributes": json.dumps({}),
                }
            )

        for out in _json_list(row.get("outcomes")):
            title = normalize_ws(str((out or {}).get("title", ""))) if isinstance(out, dict) else normalize_ws(str(out))
            timeframe = normalize_ws(str((out or {}).get("timeFrame", ""))) if isinstance(out, dict) else ""
            if not title:
                continue
            edges.append(
                {
                    "node_type_from": "trial",
                    "node_id_from": nct_id,
                    "edge_type": "PRESPECIFIES",
                    "node_type_to": "outcome_specified",
                    "node_id_to": title,
                    "attributes": json.dumps({"time_frame": timeframe}),
                }
            )

        if bool(row.get("results_posted", False)):
            edges.append(
                {
                    "node_type_from": "trial",
                    "node_id_from": nct_id,
                    "edge_type": "HAS_RESULTS_POSTED",
                    "node_type_to": "report_artifact",
                    "node_id_to": "CTGOV_RESULTS_POSTED",
                    "attributes": json.dumps({}),
                }
            )

        if bool(row.get("has_publication_link", False)):
            edges.append(
                {
                    "node_type_from": "trial",
                    "node_id_from": nct_id,
                    "edge_type": "HAS_PUBLICATION_LINK",
                    "node_type_to": "report_artifact",
                    "node_id_to": "PUBLICATION_LINKED",
                    "attributes": json.dumps({}),
                }
            )

    for df, outcome_name in ((hfhosp_df, "HF_HOSPITALIZATION"), (sae_df, "SAE")):
        if df.empty:
            continue
        for nct_id in sorted(set(df["nct_id"].astype(str))):
            edges.append(
                {
                    "node_type_from": "trial",
                    "node_id_from": nct_id,
                    "edge_type": "REPORTS",
                    "node_type_to": "outcome_reported",
                    "node_id_to": outcome_name,
                    "attributes": json.dumps({}),
                }
            )

    edge_df = pd.DataFrame(edges)
    if not edge_df.empty:
        edge_df = edge_df.drop_duplicates().reset_index(drop=True)

    trial_nodes = universe_df[[
        "nct_id",
        "brief_title",
        "overall_status",
        "primary_completion_date",
        "enrollment",
        "primary_intervention_class",
    ]].copy()
    trial_nodes = trial_nodes.rename(columns={"nct_id": "node_id", "brief_title": "label"})
    trial_nodes["node_type"] = "trial"

    class_values: List[str] = []
    for text in universe_df.get("intervention_classes", []):
        for cls in _json_list(text):
            cls = normalize_ws(str(cls))
            if cls:
                class_values.append(cls)

    class_nodes = pd.DataFrame({"node_id": sorted(set(class_values))})
    if class_nodes.empty:
        class_nodes = pd.DataFrame(columns=["node_id", "label", "node_type"])
    else:
        class_nodes["label"] = class_nodes["node_id"]
        class_nodes["node_type"] = "intervention_class"

    return GraphTables(edges=edge_df, trial_nodes=trial_nodes, class_nodes=class_nodes)
