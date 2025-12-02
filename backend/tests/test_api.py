import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys

from httpx import AsyncClient, ASGITransport

# Create mock for firebase_admin before any imports
firebase_mock = MagicMock()
firebase_mock.apps = []
firebase_mock.initialize_app = MagicMock()
firebase_mock.credential = MagicMock()
firebase_mock.credential.Certificate = MagicMock(return_value=MagicMock())
firebase_mock.auth = MagicMock()
firebase_mock.auth.verify_id_token = MagicMock(side_effect=Exception("Mock error"))
firebase_mock.get_app = MagicMock(return_value=MagicMock())
sys.modules['firebase_admin'] = firebase_mock
sys.modules['firebase_admin.auth'] = firebase_mock.auth
sys.modules['firebase_admin.credentials'] = firebase_mock.credential


# Create mock database
class MockDatabase:
    """Mock database for testing."""
    
    def __init__(self):
        self._connected = False
        self.fetch_one = AsyncMock(return_value=None)
        self.fetch_all = AsyncMock(return_value=[])
        self.execute = AsyncMock()
    
    async def connect(self):
        self._connected = True
    
    async def disconnect(self):
        self._connected = False


mock_db = MockDatabase()


@pytest.fixture(autouse=True)
def reset_mock_db():
    """Reset mock database before each test."""
    mock_db.fetch_one = AsyncMock(return_value=None)
    mock_db.fetch_all = AsyncMock(return_value=[])
    mock_db.execute = AsyncMock()
    yield


@pytest.fixture
def app_with_mock():
    """Create app with mocked database."""
    # Patch database in all model modules
    with patch('app.models.user.database', mock_db), \
         patch('app.models.book.database', mock_db), \
         patch('app.models.author.database', mock_db), \
         patch('app.models.publisher.database', mock_db), \
         patch('app.models.review.database', mock_db), \
         patch('app.models.favorite.database', mock_db), \
         patch('app.models.tag.database', mock_db), \
         patch('app.models.search_history.database', mock_db), \
         patch('app.models.user_interaction.database', mock_db), \
         patch('app.services.recommendation_service.database', mock_db), \
         patch('app.config.database.database', mock_db):
        from main import app
        yield app


@pytest.mark.asyncio
async def test_health_check(app_with_mock):
    """Test health check endpoint."""
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "timestamp" in response.json()


@pytest.mark.asyncio
async def test_unknown_route_returns_404(app_with_mock):
    """Test that unknown routes return 404."""
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/unknown")
    
    assert response.status_code == 404
    assert response.json()["error"] == "Route not found"


@pytest.mark.asyncio
async def test_get_popular_books(app_with_mock):
    """Test getting popular books."""
    mock_db.fetch_all.return_value = [
        {"id": "550e8400-e29b-41d4-a716-446655440000", "title": "Test Manga", "average_rating": 4.5}
    ]
    
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/books/popular")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_search_books(app_with_mock):
    """Test searching books."""
    mock_db.fetch_all.return_value = []
    mock_db.fetch_one.return_value = {"count": 0}
    
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/books/search?query=test")
    
    assert response.status_code == 200
    assert "books" in response.json()
    assert "total" in response.json()


@pytest.mark.asyncio
async def test_autocomplete_with_query(app_with_mock):
    """Test autocomplete with a valid query."""
    mock_db.fetch_all.return_value = [
        {"id": "550e8400-e29b-41d4-a716-446655440000", "title": "Test", "title_th": "ทดสอบ", 
         "cover_image_url": None, "type": "manga"}
    ]
    
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/books/autocomplete?query=test")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_autocomplete_short_query_returns_empty(app_with_mock):
    """Test that short autocomplete queries return empty list."""
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/books/autocomplete?query=t")
    
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_tags(app_with_mock):
    """Test getting all tags."""
    mock_db.fetch_all.return_value = [
        {"id": "550e8400-e29b-41d4-a716-446655440001", "name": "Action", "name_th": "แอคชั่น", "category": "genre"},
        {"id": "550e8400-e29b-41d4-a716-446655440002", "name": "Romance", "name_th": "โรแมนซ์", "category": "genre"},
    ]
    
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/books/tags")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_popular_tags(app_with_mock):
    """Test getting popular tags."""
    mock_db.fetch_all.return_value = [
        {"id": "550e8400-e29b-41d4-a716-446655440001", "name": "Action", "name_th": None, 
         "category": "genre", "book_count": 100}
    ]
    
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/books/tags/popular")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_authors(app_with_mock):
    """Test getting all authors."""
    mock_db.fetch_all.return_value = [
        {"id": "550e8400-e29b-41d4-a716-446655440001", "name": "Test Author", "name_th": None, 
         "biography": None, "biography_th": None, "avatar_url": None, "book_count": 5, 
         "created_at": None, "updated_at": None}
    ]
    mock_db.fetch_one.return_value = {"count": 1}
    
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/authors")
    
    assert response.status_code == 200
    assert "authors" in response.json()


@pytest.mark.asyncio
async def test_search_authors(app_with_mock):
    """Test searching authors."""
    mock_db.fetch_all.return_value = [
        {"id": "550e8400-e29b-41d4-a716-446655440001", "name": "Test", "name_th": None, 
         "biography": None, "biography_th": None, "avatar_url": None, "book_count": 0, 
         "created_at": None, "updated_at": None}
    ]
    
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/authors/search?query=test")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_publishers(app_with_mock):
    """Test getting all publishers."""
    mock_db.fetch_all.return_value = [
        {"id": "550e8400-e29b-41d4-a716-446655440001", "name": "Test Publisher", "name_th": None, 
         "description": None, "description_th": None, "website_url": None, "logo_url": None, 
         "book_count": 10, "created_at": None, "updated_at": None}
    ]
    mock_db.fetch_one.return_value = {"count": 1}
    
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/publishers")
    
    assert response.status_code == 200
    assert "publishers" in response.json()


@pytest.mark.asyncio
async def test_get_popular_recommendations(app_with_mock):
    """Test getting popular books for cold start."""
    mock_db.fetch_all.return_value = [
        {"id": "550e8400-e29b-41d4-a716-446655440001", "title": "Popular Manga", "average_rating": 4.8}
    ]
    
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/recommendations/popular")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_popular_searches(app_with_mock):
    """Test getting popular searches."""
    mock_db.fetch_all.return_value = [
        {"search_query": "one piece", "search_count": 100}
    ]
    
    transport = ASGITransport(app=app_with_mock)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/recommendations/searches/popular")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
