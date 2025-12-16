from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_book_content_by_chapter_and_section():
    """Test getting book content by chapter and section."""
    # This test will work with the sample content we initialized
    response = client.get("/api/v1/book/content?chapter=1&section=1.1")
    assert response.status_code == 200

    data = response.json()
    assert "title" in data
    assert "content" in data
    assert "chapter" in data
    assert data["chapter"] == "1"
    assert data["section"] == "1.1"

def test_get_book_content_by_chapter():
    """Test getting book content by chapter only."""
    response = client.get("/api/v1/book/content?chapter=1")
    assert response.status_code == 200

    data = response.json()
    assert "title" in data
    assert "content" in data
    assert "chapter" in data
    assert data["chapter"] == "1"

def test_get_chapter_content():
    """Test getting all content for a specific chapter."""
    response = client.get("/api/v1/book/chapter/1")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "title" in data[0]
    assert "content" in data[0]
    assert data[0]["chapter"] == "1"

def test_search_book_content():
    """Test searching for book content."""
    response = client.get("/api/v1/book/search?query=robotics")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

def test_get_all_book_content():
    """Test getting all book content."""
    response = client.get("/api/v1/book/all")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0