"""Transport-only fixtures; no synthetic clinical identifiers or findings."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from hfpef_registry_synth.ctgov_client import CTGovClient, CTGOV_API_BASE


@pytest.fixture
def client(tmp_path):
    return CTGovClient(tmp_path / "cache", sleep_seconds=0)


def fake_pages(client, monkeypatch, pages):
    calls = []
    def request(url, params=None):
        calls.append(deepcopy(params))
        assert len(calls) <= len(pages), "pagination did not terminate"
        return pages[len(calls) - 1]
    monkeypatch.setattr(client, "_request_json", request)
    return calls


def test_two_pages_preserve_query_and_caller_params(client, monkeypatch):
    params = {"query.term": "aspirin", "pageSize": 1}
    original = dict(params)
    calls = fake_pages(client, monkeypatch, [
        {"studies": [{"fixture": "first"}], "nextPageToken": "next-token"},
        {"studies": [{"fixture": "second"}]},
    ])
    assert client.query_studies(params) == [{"fixture": "first"}, {"fixture": "second"}]
    assert params == original
    assert calls[1]["query.term"] == "aspirin"
    assert calls[1]["pageToken"] == "next-token"


@pytest.mark.parametrize("page", [[], {}, {"error": "service unavailable"},
                                  {"studies": None}, {"studies": {}},
                                  {"studies": [None]}, {"studies": [], "nextPageToken": 7},
                                  {"studies": [], "nextPageToken": ""}])
def test_malformed_pages_rejected(client, monkeypatch, page):
    fake_pages(client, monkeypatch, [page])
    with pytest.raises(ValueError):
        client.query_studies({})


def test_repeated_token_rejected_before_another_request(client, monkeypatch):
    calls = fake_pages(client, monkeypatch, [{"studies": [], "nextPageToken": "same"}] * 2)
    with pytest.raises(ValueError, match="token"):
        client.query_studies({})
    assert len(calls) == 2


def test_invalid_live_page_is_not_cached(client, monkeypatch):
    response = SimpleNamespace(status_code=200, url=CTGOV_API_BASE,
                               raise_for_status=lambda: None,
                               json=lambda: {"error": "not a studies page"})
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: response)
    with pytest.raises(ValueError):
        client.query_studies({})
    assert not list(client.cache.cache_dir.glob("*.json"))


def test_invalid_cached_page_is_rejected(client):
    params = {"pageSize": 100, "countTotal": "true"}
    client.cache.set(client._cache_key(CTGOV_API_BASE, params), {"error": "bad cache"})
    with pytest.raises(ValueError):
        client.query_studies({})


def test_detail_failure_cannot_return_shallow_results(client, monkeypatch):
    fixture = Path(__file__).parent / "fixtures" / "mock_studies.json"
    study = json.loads(fixture.read_text(encoding="utf-8"))["studies"][0]
    monkeypatch.setattr(client, "query_studies", lambda params: [study])
    def fail_detail(nct_id):
        raise RuntimeError("transport fixture failure")
    monkeypatch.setattr(client, "fetch_study", fail_detail)
    with pytest.raises(RuntimeError, match="detail"):
        client.search_hfpef_trials(fetch_detail=True)
    assert client.search_hfpef_trials(fetch_detail=False) == [study]
