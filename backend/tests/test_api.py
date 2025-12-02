import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, AsyncMock

# Mock database before importing app
with patch('app.config.database.engine'):
    with patch('app.config.database.async_session_maker'):
        from app.main import app


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


@pytest.mark.anyio
async def test_root_endpoint(client):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.anyio
async def test_not_found_route(client):
    """Test 404 for unknown routes."""
    response = await client.get("/api/unknown")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_docs_available(client):
    """Test that API docs are available."""
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_openapi_schema(client):
    """Test that OpenAPI schema is available."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "paths" in data
    assert "openapi" in data
