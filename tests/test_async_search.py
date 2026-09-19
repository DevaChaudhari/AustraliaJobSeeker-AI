import time

from fastapi.testclient import TestClient

from australiajobseeker.api import main


def test_async_search_flow(monkeypatch):
    monkeypatch.setattr(main, "_run_search", lambda data: {"total_jobs": 1, "jobs": []})
    client = TestClient(main.app)

    started = client.post(
        "/search-jobs/async",
        json={"role": "AI Engineer", "location": "Sydney", "visa_type": "485"},
    )
    assert started.status_code == 202
    job_id = started.json()["job_id"]

    for _ in range(50):
        body = client.get(f"/search-jobs/{job_id}").json()
        if body["status"] != "running":
            break
        time.sleep(0.05)

    assert body["status"] == "done"
    assert body["result"]["total_jobs"] == 1


def test_async_search_validates_and_404s():
    client = TestClient(main.app)
    assert client.post("/search-jobs/async", json={"role": "x"}).status_code == 400
    assert client.get("/search-jobs/nope").status_code == 404


def test_cors_headers_present():
    client = TestClient(main.app)
    res = client.get("/health", headers={"Origin": "https://example.amplifyapp.com"})
    assert res.headers.get("access-control-allow-origin") == "*"
