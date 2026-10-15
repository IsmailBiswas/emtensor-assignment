from fastapi.testclient import TestClient

from app.main import app


def test_progress_and_dependency_endpoints() -> None:
    with TestClient(app) as client:
        progress = client.get("/api/progress")
        assert progress.status_code == 200
        body = progress.json()
        assert len(body["milestones"]) == 6
        assert len(body["tranches"]) == 4
        assert any(t["tranche_id"] == "T3" for t in body["tranches"])

        tasks = client.get("/api/dependencies/tasks")
        assert tasks.status_code == 200
        graph = tasks.json()
        assert len(graph["nodes"]) > 10
        assert len(graph["edges"]) > 10
        assert len(graph["levels"]) >= 2

        components = client.get("/api/dependencies/components")
        assert components.status_code == 200
        assert len(components.json()["edges"]) > 0

        people = client.get("/api/people")
        assert people.status_code == 200
        assert people.json()["total"] == 61

        anomalies = client.get("/api/anomalies")
        assert anomalies.status_code == 200
        assert anomalies.json()["total"] > 10
