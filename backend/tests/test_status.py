from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_status_endpoint():
    """Test the status endpoint returns expected response."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200

    data = response.json()
    assert "version" in data
    assert "uptime" in data
    assert "requests_processed" in data
    assert "environment" in data
    assert data["version"] == "0.1.0"
    assert isinstance(data["requests_processed"], int)
    assert isinstance(data["environment"], str)

def test_metrics_endpoint():
    """Test the metrics endpoint returns expected response."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200

    data = response.json()
    assert "requests_processed" in data
    assert "active_connections" in data
    assert "response_time_avg" in data
    assert "error_rate" in data
    assert "environment" in data
    assert isinstance(data["requests_processed"], int)
    assert isinstance(data["active_connections"], int)
    assert isinstance(data["response_time_avg"], float)
    assert isinstance(data["error_rate"], float)
    assert isinstance(data["environment"], str)