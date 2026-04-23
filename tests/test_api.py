import pytest
from httpx import AsyncClient, ASGITransport
from eventflow.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_create_event():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/events",
            json={
                "event_type": "test_event",
                "payload": {"key": "value"},
                "user_id": "user123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["event_type"] == "test_event"
        assert "id" in data


@pytest.mark.asyncio
async def test_list_events():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/events")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_stats():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data


@pytest.mark.asyncio
async def test_get_event_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/events/99999")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"