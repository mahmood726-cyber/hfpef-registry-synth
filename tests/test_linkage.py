import pandas as pd

from hfpef_registry_synth.linkage import PublicationLinker, enrich_publication_flags
from hfpef_registry_synth.utils import parse_json_list


def test_enrich_publication_flags_defaults_when_disabled(tmp_path):
    universe_df = pd.DataFrame(
        [
            {"nct_id": "NCT_A"},
            {"nct_id": "NCT_B"},
        ]
    )
    out = enrich_publication_flags(
        universe_df=universe_df,
        cache_dir=tmp_path / "cache",
        use_pubmed=False,
        use_openalex=False,
    )
    assert set(out.columns) >= {
        "has_publication_link",
        "publication_link_source",
        "publication_link_ids",
        "publication_link_count",
    }
    assert int(out["has_publication_link"].fillna(False).astype(bool).sum()) == 0
    assert int(out["publication_link_count"].sum()) == 0


def test_enrich_publication_flags_with_mocked_pubmed_openalex(monkeypatch, tmp_path):
    universe_df = pd.DataFrame(
        [
            {"nct_id": "NCT_A"},
            {"nct_id": "NCT_B"},
        ]
    )

    def fake_pubmed(self, nct_id: str):
        return ["11111111"] if nct_id == "NCT_A" else []

    def fake_lookup_openalex_ids(self, pmids):
        return ["https://openalex.org/W111"] if pmids else []

    def fake_search_openalex_by_nct(self, nct_id: str):
        return ["https://openalex.org/W222"] if nct_id == "NCT_B" else []

    monkeypatch.setattr(PublicationLinker, "search_pubmed_pmids", fake_pubmed)
    monkeypatch.setattr(PublicationLinker, "lookup_openalex_ids", fake_lookup_openalex_ids)
    monkeypatch.setattr(PublicationLinker, "search_openalex_by_nct", fake_search_openalex_by_nct)

    out = enrich_publication_flags(
        universe_df=universe_df,
        cache_dir=tmp_path / "cache",
        use_pubmed=True,
        use_openalex=True,
    )
    row_a = out[out["nct_id"] == "NCT_A"].iloc[0]
    row_b = out[out["nct_id"] == "NCT_B"].iloc[0]

    assert bool(row_a["has_publication_link"])
    assert row_a["publication_link_source"] == "pubmed+openalex"
    ids_a = parse_json_list(row_a["publication_link_ids"])
    assert "PMID:11111111" in ids_a
    assert "OPENALEX:https://openalex.org/W111" in ids_a

    assert not bool(row_b["has_publication_link"])
    assert row_b["publication_link_source"] == ""
    assert parse_json_list(row_b["publication_link_ids"]) == []


def test_enrich_publication_flags_openalex_only_uses_nct_search(monkeypatch, tmp_path):
    universe_df = pd.DataFrame([{"nct_id": "NCT_B"}])

    monkeypatch.setattr(PublicationLinker, "search_openalex_by_nct", lambda self, nct_id: ["https://openalex.org/W222"])

    out = enrich_publication_flags(
        universe_df=universe_df,
        cache_dir=tmp_path / "cache",
        use_pubmed=False,
        use_openalex=True,
    )
    row = out.iloc[0]
    assert bool(row["has_publication_link"])
    assert row["publication_link_source"] == "openalex"
    assert "OPENALEX:https://openalex.org/W222" in parse_json_list(row["publication_link_ids"])
