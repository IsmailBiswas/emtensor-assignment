from fastapi.testclient import TestClient

from app.main import app


def test_overview_returns_project_slices() -> None:
    with TestClient(app) as client:
        response = client.get("/api/overview")
    assert response.status_code == 200
    body = response.json()
    assert body["as_of"] == "2026-09-15"
    assert body["grant_total_inr"] > 0
    assert len(body["departments"]) == 8
    assert len(body["milestones"]) == 6
    assert len(body["tranches"]) == 4
    assert body["people_total"] == 61
