import pytest
from fastapi.testclient import TestClient

from australiajobseeker.api import main


@pytest.fixture
def client():
    return TestClient(main.app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_resume_requires_job_description(client):
    response = client.post("/generate-resume", json={"resume_text": "x"})
    assert response.status_code == 400


def test_generate_cover_letter_reports_missing_fields(client):
    response = client.post("/generate-cover-letter", json={"job_description": "x"})
    assert response.status_code == 400
    assert "company" in response.json()["detail"]


def test_generate_resume_uses_default_resume_and_agent(client, monkeypatch):
    seen = {}

    def fake_tailor(resume_text, job_description):
        seen["resume"] = resume_text
        return "tailored"

    monkeypatch.setattr(main, "tailor_resume", fake_tailor)
    response = client.post("/generate-resume", json={"job_description": "Python role"})

    assert response.json() == {"resume": "tailored"}
    assert seen["resume"].strip()  # bundled sample resume was loaded
