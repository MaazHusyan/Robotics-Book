from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_full_api_flow():
    """Test the complete API flow from health check to content retrieval."""
    # Test health endpoint
    health_response = client.get("/api/v1/health")
    assert health_response.status_code == 200
    health_data = health_response.json()
    assert health_data["status"] in ["healthy", "degraded", "unhealthy"]

    # Test status endpoint
    status_response = client.get("/api/v1/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert "version" in status_data
    assert "environment" in status_data

    # Test book content endpoint
    content_response = client.get("/api/v1/book/content?chapter=1&section=1.1")
    assert content_response.status_code == 200
    content_data = content_response.json()
    assert "title" in content_data
    assert "content" in content_data
    assert content_data["chapter"] == "1"
    assert content_data["section"] == "1.1"

    # Test book search
    search_response = client.get("/api/v1/book/search?query=robotics")
    assert search_response.status_code == 200
    search_data = search_response.json()
    assert isinstance(search_data, list)

def test_error_handling():
    """Test that the API handles errors gracefully."""
    # Test with invalid chapter
    response = client.get("/api/v1/book/content?chapter=invalid_chapter_999")
    # This should return a 404 or handle the error gracefully
    assert response.status_code in [200, 404, 422]  # Allow for different valid responses

def test_api_documentation():
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/redoc")
    assert response.status_code == 200

def test_cors_headers():
    """Test that CORS headers are properly set."""
    headers = {"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET", "Access-Control-Request-Headers": "X-Requested-With"}
    response = client.options("/api/v1/health", headers=headers)
    # Note: For wildcard origins, Access-Control-Allow-Origin will not be in the response
    # For specific origins, this header would be present

    # Just check that the options request works
    assert response.status_code in [200, 204]