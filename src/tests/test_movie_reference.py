import pytest
import pytest_asyncio
from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient

from main import app

from dependencies.movies import (
    get_certification_service,
    get_director_service,
    get_genre_service,
    get_star_service,
)


@pytest.fixture
def mock_service():
    return AsyncMock()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture(autouse=True)
def reset_dependency_overrides():
    yield
    app.dependency_overrides.clear()


# ==================== CERTIFICATIONS ====================

@pytest.mark.asyncio
async def test_create_certification(client, mock_service):
    app.dependency_overrides[get_certification_service] = lambda: mock_service
    mock_service.is_admin.return_value = True
    mock_service.create_certification.return_value = {"id": 1, "name": "Test"}

    response = await client.post(
        "/api/v1/certifications/",
        json={"name": "Test"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == 1
    mock_service.create_certification.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_certification_forbidden(client, mock_service):
    app.dependency_overrides[get_certification_service] = lambda: mock_service
    mock_service.is_admin.return_value = False

    response = await client.post(
        "/api/v1/certifications/",
        json={"name": "Test"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You haven't appropriate permission"
    mock_service.create_certification.assert_not_awaited()


@pytest.mark.asyncio
async def test_read_certification(client, mock_service):
    app.dependency_overrides[get_certification_service] = lambda: mock_service
    mock_service.get_certification.return_value = {"id": 1, "name": "Test"}

    response = await client.get("/api/v1/certifications/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_read_certification_not_found(client, mock_service):
    app.dependency_overrides[get_certification_service] = lambda: mock_service
    mock_service.get_certification.return_value = None

    response = await client.get("/api/v1/certifications/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Certification not found"


@pytest.mark.asyncio
async def test_read_all_certifications(client, mock_service):
    app.dependency_overrides[get_certification_service] = lambda: mock_service
    mock_service.get_all_certifications.return_value = [
        {"id": 1, "name": "Test 1"},
        {"id": 2, "name": "Test 2"},
    ]

    response = await client.get("/api/v1/certifications/")

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_delete_certification(client, mock_service):
    app.dependency_overrides[get_certification_service] = lambda: mock_service
    mock_service.is_admin.return_value = True
    mock_service.delete_certification.return_value = {"id": 1, "name": "Test"}

    response = await client.delete("/api/v1/certifications/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_delete_certification_forbidden(client, mock_service):
    app.dependency_overrides[get_certification_service] = lambda: mock_service
    mock_service.is_admin.return_value = False

    response = await client.delete("/api/v1/certifications/1")

    assert response.status_code == 403
    mock_service.delete_certification.assert_not_awaited()


# ==================== DIRECTORS ====================

@pytest.mark.asyncio
async def test_create_director(client, mock_service):
    app.dependency_overrides[get_director_service] = lambda: mock_service
    mock_service.is_admin.return_value = True
    mock_service.create_director.return_value = {"id": 1, "name": "Test"}

    response = await client.post(
        "/api/v1/directors/",
        json={"name": "Test"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == 1
    mock_service.create_director.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_director_forbidden(client, mock_service):
    app.dependency_overrides[get_director_service] = lambda: mock_service
    mock_service.is_admin.return_value = False

    response = await client.post(
        "/api/v1/directors/",
        json={"name": "Test"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You haven't appropriate permission"
    mock_service.create_director.assert_not_awaited()


@pytest.mark.asyncio
async def test_read_director(client, mock_service):
    app.dependency_overrides[get_director_service] = lambda: mock_service
    mock_service.get_director.return_value = {"id": 1, "name": "Test"}

    response = await client.get("/api/v1/directors/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_read_director_not_found(client, mock_service):
    app.dependency_overrides[get_director_service] = lambda: mock_service
    mock_service.get_director.return_value = None

    response = await client.get("/api/v1/directors/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Director not found"


@pytest.mark.asyncio
async def test_read_all_directors(client, mock_service):
    app.dependency_overrides[get_director_service] = lambda: mock_service
    mock_service.get_all_directors.return_value = [
        {"id": 1, "name": "Test 1"},
        {"id": 2, "name": "Test 2"},
    ]

    response = await client.get("/api/v1/directors/")

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_delete_director(client, mock_service):
    app.dependency_overrides[get_director_service] = lambda: mock_service
    mock_service.is_admin.return_value = True
    mock_service.delete_director.return_value = {"id": 1, "name": "Test"}

    response = await client.delete("/api/v1/directors/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_delete_director_forbidden(client, mock_service):
    app.dependency_overrides[get_director_service] = lambda: mock_service
    mock_service.is_admin.return_value = False

    response = await client.delete("/api/v1/directors/1")

    assert response.status_code == 403
    mock_service.delete_director.assert_not_awaited()


# ==================== GENRES ====================

@pytest.mark.asyncio
async def test_create_genre(client, mock_service):
    app.dependency_overrides[get_genre_service] = lambda: mock_service
    mock_service.is_admin.return_value = True
    mock_service.create_genre.return_value = {"id": 1, "name": "Test"}

    response = await client.post(
        "/api/v1/genres/",
        json={"name": "Test"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == 1
    mock_service.create_genre.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_genre_forbidden(client, mock_service):
    app.dependency_overrides[get_genre_service] = lambda: mock_service
    mock_service.is_admin.return_value = False

    response = await client.post(
        "/api/v1/genres/",
        json={"name": "Test"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You haven't appropriate permission"
    mock_service.create_genre.assert_not_awaited()


@pytest.mark.asyncio
async def test_read_genre(client, mock_service):
    app.dependency_overrides[get_genre_service] = lambda: mock_service
    mock_service.get_genre.return_value = {"id": 1, "name": "Test"}

    response = await client.get("/api/v1/genres/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_read_genre_not_found(client, mock_service):
    app.dependency_overrides[get_genre_service] = lambda: mock_service
    mock_service.get_genre.return_value = None

    response = await client.get("/api/v1/genres/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Genre not found"


@pytest.mark.asyncio
async def test_read_all_genres(client, mock_service):
    app.dependency_overrides[get_genre_service] = lambda: mock_service
    mock_service.get_all_genres.return_value = [
        {"id": 1, "name": "Test 1"},
        {"id": 2, "name": "Test 2"},
    ]

    response = await client.get("/api/v1/genres/")

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_delete_genre(client, mock_service):
    app.dependency_overrides[get_genre_service] = lambda: mock_service
    mock_service.is_admin.return_value = True
    mock_service.delete_genre.return_value = {"id": 1, "name": "Test"}

    response = await client.delete("/api/v1/genres/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_delete_genre_forbidden(client, mock_service):
    app.dependency_overrides[get_genre_service] = lambda: mock_service
    mock_service.is_admin.return_value = False

    response = await client.delete("/api/v1/genres/1")

    assert response.status_code == 403
    mock_service.delete_genre.assert_not_awaited()


# ==================== STARS ====================

@pytest.mark.asyncio
async def test_create_star(client, mock_service):
    app.dependency_overrides[get_star_service] = lambda: mock_service
    mock_service.is_admin.return_value = True
    mock_service.create_star.return_value = {"id": 1, "name": "Test"}

    response = await client.post(
        "/api/v1/stars/",
        json={"name": "Test"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == 1
    mock_service.create_star.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_star_forbidden(client, mock_service):
    app.dependency_overrides[get_star_service] = lambda: mock_service
    mock_service.is_admin.return_value = False

    response = await client.post(
        "/api/v1/stars/",
        json={"name": "Test"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You haven't appropriate permission"
    mock_service.create_star.assert_not_awaited()


@pytest.mark.asyncio
async def test_read_star(client, mock_service):
    app.dependency_overrides[get_star_service] = lambda: mock_service
    mock_service.get_star.return_value = {"id": 1, "name": "Test"}

    response = await client.get("/api/v1/stars/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_read_star_not_found(client, mock_service):
    app.dependency_overrides[get_star_service] = lambda: mock_service
    mock_service.get_star.return_value = None

    response = await client.get("/api/v1/stars/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Star not found"


@pytest.mark.asyncio
async def test_read_all_stars(client, mock_service):
    app.dependency_overrides[get_star_service] = lambda: mock_service
    mock_service.get_all_stars.return_value = [
        {"id": 1, "name": "Test 1"},
        {"id": 2, "name": "Test 2"},
    ]

    response = await client.get("/api/v1/stars/")

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_delete_star(client, mock_service):
    app.dependency_overrides[get_star_service] = lambda: mock_service
    mock_service.is_admin.return_value = True
    mock_service.delete_star.return_value = {"id": 1, "name": "Test"}

    response = await client.delete("/api/v1/stars/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.asyncio
async def test_delete_star_forbidden(client, mock_service):
    app.dependency_overrides[get_star_service] = lambda: mock_service
    mock_service.is_admin.return_value = False

    response = await client.delete("/api/v1/stars/1")

    assert response.status_code == 403
    mock_service.delete_star.assert_not_awaited()
