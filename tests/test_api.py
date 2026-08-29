from fastapi.testclient import TestClient
from worldvision_ai_project.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "worldvision-ai-project",
        "version": "0.1.0",
    }


def test_search_empty_query():
    response = client.post(
        "/api/v1/search",
        json={"query": ""},
    )

    assert response.status_code == 422


def test_report_empty_topic():
    response = client.post(
        "/api/v1/report",
        json={"topic": ""},
    )

    assert response.status_code == 422


def test_minutes_invalid_file_extension():
    response = client.post(
        "/api/v1/minutes",
        files={"file": ("test.txt", b"test audio data", "text/plain")},
    )

    assert response.status_code == 400