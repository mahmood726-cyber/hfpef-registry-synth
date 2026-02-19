"""ClinicalTrials.gov v2 API client with caching and retry logic."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests
from tqdm import tqdm

from .cache import DiskCache
from .logging_utils import setup_logging

CTGOV_API_BASE = "https://clinicaltrials.gov/api/v2/studies"
HFPEF_TERMS = [
    "HFpEF",
    "heart failure with preserved ejection fraction",
    "preserved ejection fraction",
    "diastolic heart failure",
]


class CTGovClient:
    """Thin client for CT.gov v2 with deterministic disk caching."""

    def __init__(
        self,
        cache_dir: Path,
        timeout: int = 30,
        max_retries: int = 4,
        sleep_seconds: float = 0.2,
    ) -> None:
        self.cache = DiskCache(cache_dir)
        self.timeout = timeout
        self.max_retries = max_retries
        self.sleep_seconds = sleep_seconds
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "hfpef-registry-synth/0.1.0",
            }
        )
        self.logger = setup_logging(name="hfpef_registry_synth.ctgov")

    def _cache_key(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
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
                return data
            except Exception as exc:  # pragma: no cover - network behavior
                last_error = exc
                delay = (2**attempt) * self.sleep_seconds
                self.logger.warning("Request failed (%s). Retry in %.2fs", exc, delay)
                time.sleep(delay)

        raise RuntimeError(f"CT.gov request failed after retries: {url} ({last_error})")

    def fetch_study(self, nct_id: str) -> Dict[str, Any]:
        url = f"{CTGOV_API_BASE}/{nct_id}"
        return self._request_json(url)

    def iter_query_pages(self, params: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        req = dict(params)
        req.setdefault("pageSize", 100)
        req.setdefault("countTotal", "true")

        while True:
            page = self._request_json(CTGOV_API_BASE, req)
            yield page
            token = page.get("nextPageToken")
            if not token:
                break
            req["pageToken"] = token
            req.pop("countTotal", None)

    def query_studies(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        studies: List[Dict[str, Any]] = []
        for page in self.iter_query_pages(params):
            studies.extend(page.get("studies", []))
            time.sleep(self.sleep_seconds)
        return studies

    @staticmethod
    def _nct_id(study: Dict[str, Any]) -> str:
        return (
            study.get("protocolSection", {})
            .get("identificationModule", {})
            .get("nctId", "")
            .upper()
        )

    def search_hfpef_trials(self, fetch_detail: bool = True) -> List[Dict[str, Any]]:
        """Run multiple HFpEF registry-first queries and deduplicate by NCT."""
        query_specs = [
            {
                "query.cond": "heart failure",
                "query.term": "(HFpEF OR preserved ejection fraction OR diastolic heart failure) AND AREA[StudyType]INTERVENTIONAL",
            },
            {
                "query.term": "(HFpEF OR heart failure with preserved ejection fraction OR preserved ejection fraction OR diastolic heart failure) AND AREA[StudyType]INTERVENTIONAL",
            },
            {
                "query.term": "AREA[DesignAllocation]RANDOMIZED AND (HFpEF OR preserved ejection fraction)",
            },
        ]

        all_studies: Dict[str, Dict[str, Any]] = {}
        for spec in query_specs:
            self.logger.info("Querying CT.gov with params=%s", spec)
            for study in self.query_studies(spec):
                nct_id = self._nct_id(study)
                if nct_id:
                    all_studies[nct_id] = study

        # Additional term-wise search to improve recall.
        for term in HFPEF_TERMS:
            spec = {
                "query.term": f"{term} AND AREA[StudyType]INTERVENTIONAL",
            }
            for study in self.query_studies(spec):
                nct_id = self._nct_id(study)
                if nct_id:
                    all_studies[nct_id] = study

        studies = list(all_studies.values())
        self.logger.info("Collected %d unique studies before detail hydration", len(studies))

        if not fetch_detail:
            return studies

        hydrated: List[Dict[str, Any]] = []
        for study in tqdm(studies, desc="Hydrating studies", unit="study"):
            nct_id = self._nct_id(study)
            if not nct_id:
                continue
            try:
                full = self.fetch_study(nct_id)
                hydrated.append(full)
            except Exception as exc:  # pragma: no cover - network behavior
                self.logger.warning("Falling back to shallow record for %s: %s", nct_id, exc)
                hydrated.append(study)

        return hydrated


def ctgov_record_url(nct_id: str) -> str:
    return f"https://clinicaltrials.gov/study/{nct_id}"
