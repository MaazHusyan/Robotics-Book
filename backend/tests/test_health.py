from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health endpoint returns expected response."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "dependencies" in data
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert isinstance(data["dependencies"], dict)

def test_readiness_endpoint():
    """Test the readiness endpoint returns expected response."""
    response = client.get("/api/v1/ready")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] == "ready"