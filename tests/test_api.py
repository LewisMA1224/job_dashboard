from src.job_dashboard import api


class DummyResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def test_fetch_jobs_returns_jobs_list(monkeypatch):
    captured = {}

    def fake_get(url, params, timeout):
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout
        return DummyResponse({"jobs": [{"title": "Backend Engineer"}]})

    monkeypatch.setattr(api.requests, "get", fake_get)

    jobs = api.fetch_jobs("python")

    assert isinstance(jobs, list)
    assert len(jobs) == 1
    assert captured["params"] == {"search": "python"}
    assert captured["timeout"] == 20


def test_fetch_jobs_handles_missing_jobs_key(monkeypatch):
    def fake_get(url, params, timeout):
        return DummyResponse({"status": "ok"})

    monkeypatch.setattr(api.requests, "get", fake_get)

    jobs = api.fetch_jobs("data")

    assert jobs == []
