from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns expected response."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "status" in data
    assert "version" in data
    assert "available_endpoints" in data
    assert data["message"] == "Welcome to the Robotics Book API"
    assert data["status"] == "running"
    assert data["version"] == "0.1.0"
    assert isinstance(data["available_endpoints"], list)

def test_status_endpoint():
    """Test the status endpoint returns expected response."""
    response = client.get("/status")
    assert response.status_code == 200

    data = response.json()
    assert "version" in data
    assert "uptime" in data
    assert "requests_processed" in data
    assert "environment" in data
    assert data["version"] == "0.1.0"
    assert isinstance(data["requests_processed"], int)
    assert isinstance(data["environment"], str)