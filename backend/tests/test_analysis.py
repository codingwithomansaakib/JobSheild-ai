from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_and_run_analysis():
    payload = {
        "text": "Company: Example Tech\nRole: Python Intern\nRegistration fee: ₹2999\nhr@example@gmail.com",
        "source_url": "https://example.com/jobs/python-intern",
    }

    created = client.post("/api/v1/analyses", json=payload)
    assert created.status_code == 200

    analysis_id = created.json()["analysis_id"]
    result = client.post(f"/api/v1/analyses/{analysis_id}/run")

    assert result.status_code == 200
    assert result.json()["status"] == "COMPLETED"
    assert result.json()["risk_level"] in {"LOW", "MEDIUM", "HIGH", "UNABLE_TO_VERIFY"}
