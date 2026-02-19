"""Optional publication-linkage enrichment via open APIs."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd
import requests

from .cache import DiskCache
from .logging_utils import setup_logging
from .utils import normalize_ws, to_json_text

PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
OPENALEX_WORKS_URL = "https://api.openalex.org/works"


class PublicationLinker:
    """Link NCT IDs to open publication artifacts (PubMed/OpenAlex)."""

    def __init__(
        self,
        cache_dir: Path,
        timeout: int = 20,
        max_retries: int = 3,
        sleep_seconds: float = 0.34,
    ) -> None:
        self.cache = DiskCache(cache_dir)
        self.timeout = timeout
        self.max_retries = max_retries
        # NCBI requests should remain low frequency without an API key.
        self.sleep_seconds = max(float(sleep_seconds), 0.34)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "hfpef-registry-synth/0.1.0",
            }
        )
        self.logger = setup_logging(name="hfpef_registry_synth.linkage")

    @staticmethod
    def _cache_key(url: str, params: Optional[Dict[str, Any]] = None) -> str:
        payload = {"url": url, "params": params or {}}
        return json.dumps(payload, sort_keys=True, ensure_ascii=True)

    def _request_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        key = self._cache_key(url, params)
        cached = self.cache.get(key)
        if cached is not None:
            return cached

        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                if resp.status_code in {429, 500, 502, 503, 504}:
                    delay = (2**attempt) * self.sleep_seconds
                    self.logger.warning(
                        "Retryable status %s for %s; sleeping %.2fs",
                        resp.status_code,
                        resp.url,
                        delay,
                    )
                    time.sleep(delay)
                    continue
                resp.raise_for_status()
                data = resp.json()
                self.cache.set(key, data)
                time.sleep(self.sleep_seconds)
                return data
            except Exception as exc:  # pragma: no cover - network behavior
                last_error = exc
                delay = (2**attempt) * self.sleep_seconds
                self.logger.warning("Linkage request failed (%s). Retry in %.2fs", exc, delay)
                time.sleep(delay)

        raise RuntimeError(f"Publication-linkage request failed after retries: {url} ({last_error})")

    def search_pubmed_pmids(self, nct_id: str) -> List[str]:
        nct = normalize_ws(nct_id).upper()
        if not nct:
            return []
        term = f'("{nct}"[si]) OR ("{nct}"[tw])'
        params = {
            "db": "pubmed",
            "retmode": "json",
            "retmax": 20,
            "term": term,
        }
        data = self._request_json(PUBMED_ESEARCH_URL, params=params)
        ids = data.get("esearchresult", {}).get("idlist", []) or []
        out: List[str] = []
        for item in ids:
            pmid = normalize_ws(str(item))
            if pmid and pmid not in out:
                out.append(pmid)
        return out

    def lookup_openalex_ids(self, pmids: Sequence[str]) -> List[str]:
        out: List[str] = []
        # Keep this to one PMID lookup for speed and API stability.
        for pmid in pmids[:1]:
            key = normalize_ws(str(pmid))
            if not key:
                continue
            params = {"filter": f"pmid:{key}", "per-page": 5}
            data = self._request_json(OPENALEX_WORKS_URL, params=params)
            for item in data.get("results", []) or []:
                wid = normalize_ws(str(item.get("id", "")))
                if wid and wid not in out:
                    out.append(wid)
        return out

    def search_openalex_by_nct(self, nct_id: str) -> List[str]:
        nct = normalize_ws(nct_id).upper()
        if not nct:
            return []
        params = {"search": nct, "per-page": 10}
        data = self._request_json(OPENALEX_WORKS_URL, params=params)
        out: List[str] = []
        token = nct.lower()
        for item in data.get("results", []) or []:
            wid = normalize_ws(str(item.get("id", "")))
            title = normalize_ws(str(item.get("display_name", ""))).lower()
            ids = item.get("ids", {}) if isinstance(item, dict) else {}
            doi = normalize_ws(str(ids.get("doi", "") if isinstance(ids, dict) else "")).lower()
            pmid = normalize_ws(str(ids.get("pmid", "") if isinstance(ids, dict) else "")).lower()
            haystack = " ".join([title, doi, pmid])
            if wid and token in haystack and wid not in out:
                out.append(wid)
        return out


def enrich_publication_flags(
    universe_df: pd.DataFrame,
    cache_dir: Path,
    use_pubmed: bool,
    use_openalex: bool,
    timeout: int = 20,
    max_retries: int = 3,
    sleep_seconds: float = 0.34,
) -> pd.DataFrame:
    out = universe_df.copy()
    out["has_publication_link"] = False
    out["publication_link_source"] = ""
    out["publication_link_ids"] = "[]"
    out["publication_link_count"] = 0

    if out.empty or not (use_pubmed or use_openalex):
        return out

    linker = PublicationLinker(
        cache_dir=cache_dir / "linkage",
        timeout=timeout,
        max_retries=max_retries,
        sleep_seconds=sleep_seconds,
    )

    total = int(len(out))
    for i, (idx, row) in enumerate(out.iterrows(), start=1):
        nct_id = normalize_ws(str(row.get("nct_id", ""))).upper()
        if not nct_id:
            continue

        sources: List[str] = []
        link_ids: List[str] = []

        pmids: List[str] = []
        if use_pubmed:
            try:
                pmids = linker.search_pubmed_pmids(nct_id)
            except Exception as exc:  # pragma: no cover - network behavior
                linker.logger.warning("PubMed linkage failed for %s: %s", nct_id, exc)
                pmids = []
            if pmids:
                sources.append("pubmed")
                link_ids.extend([f"PMID:{x}" for x in pmids])

        openalex_ids: List[str] = []
        if use_openalex:
            try:
                if pmids:
                    openalex_ids = linker.lookup_openalex_ids(pmids)
                elif not use_pubmed:
                    openalex_ids = linker.search_openalex_by_nct(nct_id)
            except Exception as exc:  # pragma: no cover - network behavior
                linker.logger.warning("OpenAlex linkage failed for %s: %s", nct_id, exc)
                openalex_ids = []
            if openalex_ids:
                sources.append("openalex")
                link_ids.extend([f"OPENALEX:{x}" for x in openalex_ids])

        link_ids = sorted(set(link_ids))
        has_link = bool(link_ids)
        out.at[idx, "has_publication_link"] = has_link
        out.at[idx, "publication_link_source"] = "+".join(sources)
        out.at[idx, "publication_link_ids"] = to_json_text(link_ids)
        out.at[idx, "publication_link_count"] = int(len(link_ids))

        if i % 25 == 0 or i == total:
            linker.logger.info("Publication linkage progress: %d/%d", i, total)

    return out
