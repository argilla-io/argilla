import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_route_not_found_response(async_client: AsyncClient):
    response = await async_client.get("/api/not-found-route")

    assert response.status_code == 404
    assert response.json() == {"detail": "Endpoint '/api/not-found-route' not found"}
