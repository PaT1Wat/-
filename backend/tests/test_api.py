import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport

# Mock Firebase before importing app
firebase_mock = MagicMock()
firebase_mock.apps = []
firebase_mock.initialize_app = MagicMock()
firebase_mock.credential.Certificate = MagicMock()
firebase_mock.auth.return_value.verify_id_token = MagicMock(side_effect=Exception("Mock error"))

with patch.dict('sys.modules', {'firebase_admin': firebase_mock}):
    from main import app


@pytest.fixture
def mock_database():
    """Mock database for testing."""
    with patch('app.config.database.database') as mock_db:
        mock_db.fetch_one = AsyncMock(return_value=None)
        mock_db.fetch_all = AsyncMock(return_value=[])
        mock_db.execute = AsyncMock()
        mock_db.connect = AsyncMock()
        mock_db.disconnect = AsyncMock()
        yield mock_db


@pytest.mark.asyncio
async def test_health_check(mock_database):
    """Test health check endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "timestamp" in response.json()


@pytest.mark.asyncio
async def test_unknown_route_returns_404(mock_database):
    """Test that unknown routes return 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/unknown")
    
    assert response.status_code == 404
    assert response.json()["error"] == "Route not found"


@pytest.mark.asyncio
async def test_get_popular_books(mock_database):
    """Test getting popular books."""
    mock_database.fetch_all.return_value = [
        {"id": "test-id-1", "title": "Test Manga", "average_rating": 4.5}
    ]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/books/popular")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_search_books(mock_database):
    """Test searching books."""
    mock_database.fetch_all.return_value = []
    mock_database.fetch_one.return_value = {"count": 0}
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/books/search?query=test")
    
    assert response.status_code == 200
    assert "books" in response.json()
    assert "total" in response.json()


@pytest.mark.asyncio
async def test_autocomplete_with_query(mock_database):
    """Test autocomplete with a valid query."""
    mock_database.fetch_all.return_value = [
        {"id": "test-id-1", "title": "Test", "title_th": "ทดสอบ", "cover_image_url": None, "type": "manga"}
    ]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/books/autocomplete?query=test")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_autocomplete_short_query_returns_empty(mock_database):
    """Test that short autocomplete queries return empty list."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/books/autocomplete?query=t")
    
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_tags(mock_database):
    """Test getting all tags."""
    mock_database.fetch_all.return_value = [
        {"id": "tag-1", "name": "Action", "name_th": "แอคชั่น", "category": "genre"},
        {"id": "tag-2", "name": "Romance", "name_th": "โรแมนซ์", "category": "genre"},
    ]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/books/tags")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_popular_tags(mock_database):
    """Test getting popular tags."""
    mock_database.fetch_all.return_value = [
        {"id": "tag-1", "name": "Action", "name_th": None, "category": "genre", "book_count": 100}
    ]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/books/tags/popular")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_authors(mock_database):
    """Test getting all authors."""
    mock_database.fetch_all.return_value = [
        {"id": "author-1", "name": "Test Author", "name_th": None, "biography": None, 
         "biography_th": None, "avatar_url": None, "book_count": 5, "created_at": None, "updated_at": None}
    ]
    mock_database.fetch_one.return_value = {"count": 1}
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/authors")
    
    assert response.status_code == 200
    assert "authors" in response.json()


@pytest.mark.asyncio
async def test_search_authors(mock_database):
    """Test searching authors."""
    mock_database.fetch_all.return_value = [
        {"id": "author-1", "name": "Test", "name_th": None, "biography": None, 
         "biography_th": None, "avatar_url": None, "book_count": 0, "created_at": None, "updated_at": None}
    ]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/authors/search?query=test")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_publishers(mock_database):
    """Test getting all publishers."""
    mock_database.fetch_all.return_value = [
        {"id": "pub-1", "name": "Test Publisher", "name_th": None, "description": None,
         "description_th": None, "website_url": None, "logo_url": None, "book_count": 10, 
         "created_at": None, "updated_at": None}
    ]
    mock_database.fetch_one.return_value = {"count": 1}
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/publishers")
    
    assert response.status_code == 200
    assert "publishers" in response.json()


@pytest.mark.asyncio
async def test_get_popular_recommendations(mock_database):
    """Test getting popular books for cold start."""
    mock_database.fetch_all.return_value = [
        {"id": "book-1", "title": "Popular Manga", "average_rating": 4.8}
    ]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/recommendations/popular")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_popular_searches(mock_database):
    """Test getting popular searches."""
    mock_database.fetch_all.return_value = [
        {"search_query": "one piece", "search_count": 100}
    ]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/recommendations/searches/popular")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
