from fastapi.testclient import TestClient

from app.main import app


def test_data_summary_and_refresh() -> None:
    with TestClient(app) as client:
        summary = client.get("/api/data/summary")
        assert summary.status_code == 200
        body = summary.json()
        assert body["as_of"] == "2026-09-15"
        assert body["counts"]["departments"] == 8
        assert body["counts"]["components"] == 315

        refresh = client.post("/api/data/refresh")
        assert refresh.status_code == 200
        assert refresh.json()["status"] == "reloaded"
        assert refresh.json()["summary"]["counts"]["milestones"] == 6
