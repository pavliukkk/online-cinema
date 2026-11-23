import pytest
import pytest_asyncio

from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient

from database import MovieModel
from main import app as application

from dependencies.movies import (
    get_movie_service,
    get_comment_service,
)
from repositories.movies.movie import MovieRepository


@pytest.fixture
def movie_service():
    return AsyncMock()


@pytest.fixture
def comment_service():
    return AsyncMock()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
            transport=ASGITransport(app=application),
            base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture(autouse=True)
def reset_dependency_overrides():
    yield
    application.dependency_overrides.clear()


MOVIE_DATA = {
    "name": "Test Movie",
    "year": 2024,
    "time": 120,
    "imdb": 8.5,
    "votes": 1000,
    "meta_score": 85,
    "gross": 1000000,
    "description": "Test description",
    "price": "10.50",
    "genres": [1],
    "stars": [1],
    "directors": [1],
    "certification_id": 1,
}


@pytest.mark.asyncio
async def test_create_movie(client, movie_service):
    application.dependency_overrides[get_movie_service] = (
        lambda: movie_service
    )

    movie_service.is_admin.return_value = True

    movie_service.create_movie.return_value = {
        "id": 1,
        "uuid": "12345678-1234-5678-1234-567812345678",
        "name": "Test Movie",
        "year": 2024,
        "time": 120,
        "imdb": 8.5,
        "votes": 1000,
        "description": "Test movie description",
        "price": 100,
        "genres": [],
        "stars": [],
        "directors": [],
        "certification": {
            "id": 1,
            "name": "PG-13",
        },
    }

    response = await client.post(
        "/api/v1/movies/",
        json=MOVIE_DATA,
    )

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Test Movie"

    movie_service.create_movie.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_movie_forbidden(client, movie_service):
    application.dependency_overrides[get_movie_service] = (
        lambda: movie_service
    )

    movie_service.is_admin.return_value = False

    response = await client.post(
        "/api/v1/movies/",
        json=MOVIE_DATA,
    )

    assert response.status_code == 403

    movie_service.create_movie.assert_not_awaited()


@pytest.mark.asyncio
async def test_read_movie(client, movie_service):
    application.dependency_overrides[get_movie_service] = (
        lambda: movie_service
    )

    movie_service.get_movie.return_value = {
        "id": 1,
        "uuid": "12345678-1234-5678-1234-567812345678",
        "name": "Test Movie",
        "year": 2024,
        "time": 120,
        "imdb": 8.5,
        "votes": 1000,
        "description": "Test movie description",
        "price": 100,
        "genres": [],
        "stars": [],
        "directors": [],
        "certification": {
            "id": 1,
            "name": "PG-13",
        },
    }

    response = await client.get("/api/v1/movies/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Test Movie"


@pytest.mark.asyncio
async def test_read_movie_not_found(client, movie_service):
    application.dependency_overrides[get_movie_service] = (
        lambda: movie_service
    )

    movie_service.get_movie.return_value = None

    response = await client.get("/api/v1/movies/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Movie not found"


@pytest.mark.asyncio
async def test_read_movies(client, movie_service):
    application.dependency_overrides[get_movie_service] = (
        lambda: movie_service
    )

    movie_service.get_movies_with_params.return_value = {
        "movies": [],
        "prev_page": None,
        "next_page": None,
        "total_pages": 1,
        "total_items": 2,
    }

    response = await client.get("/api/v1/movies/")

    assert response.status_code == 200
    assert "movies" in response.json()
    assert response.json()["total_items"] == 2


@pytest.mark.asyncio
async def test_read_movies_with_filters(client, movie_service):
    application.dependency_overrides[get_movie_service] = (
        lambda: movie_service
    )

    movie_service.get_movies_with_params.return_value = {
        "movies": [],
        "prev_page": None,
        "next_page": None,
        "total_pages": 1,
        "total_items": 0,
    }

    response = await client.get(
        "/api/v1/movies/",
        params={
            "page": 1,
            "page_size": 10,
            "name": "Test",
            "year": 2024,
            "rating": 8.5,
            "sort_by": "rating",
        },
    )

    assert response.status_code == 200

    movie_service.get_movies_with_params.assert_awaited()


@pytest.mark.asyncio
async def test_delete_movie(client, movie_service):
    application.dependency_overrides[get_movie_service] = (
        lambda: movie_service
    )

    movie_service.is_admin.return_value = True
    movie_service.cant_delete_movie.return_value = False
    movie_service.delete_movie.return_value = {
        "id": 1,
        "uuid": "12345678-1234-5678-1234-567812345678",
        "name": "Test Movie",
        "year": 2024,
        "time": 120,
        "imdb": 8.5,
        "votes": 1000,
        "description": "Test movie description",
        "price": 100,
        "genres": [],
        "stars": [],
        "directors": [],
        "certification": {
            "id": 1,
            "name": "PG-13",
        },
    }

    response = await client.delete("/api/v1/movies/1")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_movie_forbidden(client, movie_service):
    application.dependency_overrides[get_movie_service] = (
        lambda: movie_service
    )

    movie_service.is_admin.return_value = False

    response = await client.delete("/api/v1/movies/1")

    assert response.status_code == 403

    movie_service.delete_movie.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_movie_not_found(client, movie_service):
    application.dependency_overrides[get_movie_service] = (
        lambda: movie_service
    )

    movie_service.is_admin.return_value = True
    movie_service.cant_delete_movie.return_value = False
    movie_service.delete_movie.return_value = None

    response = await client.delete("/api/v1/movies/999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_like_movie(client, movie_service):
    application.dependency_overrides[get_movie_service] = (
        lambda: movie_service
    )

    response = await client.post(
        "/api/v1/movies/1/like"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Movie liked successfully"
    }

    movie_service.like_movie.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_dislike_movie(client, movie_service):
    application.dependency_overrides[get_movie_service] = (
        lambda: movie_service
    )

    response = await client.post(
        "/api/v1/movies/1/dislike"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Movie disliked successfully"
    }

    movie_service.dislike_movie.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_increment_likes(db_session):
    movie = MovieModel(
        name="Test Movie",
        year=2024,
        time=120,
        imdb=8.5,
        votes=1000,
        description="Test description",
        price=10.50,
        certification_id=1,
    )

    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)

    repository = MovieRepository(db_session)

    await repository.increment_likes(movie.id)

    await db_session.refresh(movie)

    assert movie.likes == 1


@pytest.mark.asyncio
async def test_increment_dislikes(db_session):
    movie = MovieModel(
        name="Test Movie",
        year=2024,
        time=120,
        imdb=8.5,
        votes=1000,
        description="Test description",
        price=10.50,
        certification_id=1,
    )

    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)

    repository = MovieRepository(db_session)

    await repository.increment_dislikes(movie.id)

    await db_session.refresh(movie)

    assert movie.dislikes == 1


@pytest.mark.asyncio
async def test_increment_likes_multiple_times(db_session):
    movie = MovieModel(
        name="Test Movie",
        year=2024,
        time=120,
        imdb=8.5,
        votes=1000,
        description="Test description",
        price=10.50,
        certification_id=1,
    )

    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)

    repository = MovieRepository(db_session)

    await repository.increment_likes(movie.id)
    await repository.increment_likes(movie.id)
    await repository.increment_likes(movie.id)

    await db_session.refresh(movie)

    assert movie.likes == 3


@pytest.mark.asyncio
async def test_increment_dislikes_multiple_times(db_session):
    movie = MovieModel(
        name="Test Movie",
        year=2024,
        time=120,
        imdb=8.5,
        votes=1000,
        description="Test description",
        price=10.50,
        certification_id=1,
    )

    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)

    repository = MovieRepository(db_session)

    await repository.increment_dislikes(movie.id)
    await repository.increment_dislikes(movie.id)
    await repository.increment_dislikes(movie.id)

    await db_session.refresh(movie)

    assert movie.dislikes == 3


@pytest.mark.asyncio
async def test_increment_likes_movie_not_found(db_session):
    repository = MovieRepository(db_session)

    with pytest.raises(Exception):
        await repository.increment_likes(999999)


@pytest.mark.asyncio
async def test_increment_dislikes_movie_not_found(db_session):
    repository = MovieRepository(db_session)

    with pytest.raises(Exception):
        await repository.increment_dislikes(999999)


@pytest.mark.asyncio
async def test_rate_movie(client, movie_service):
    application.dependency_overrides[get_movie_service] = (
        lambda: movie_service
    )

    response = await client.post(
        "/api/v1/movies/1/rate",
        params={"user_rating": 8.5},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Movie rated successfully"
    }

    movie_service.rate_movie.assert_awaited_once_with(1, 8.5)


@pytest.mark.parametrize(
    "rating",
    [0, 11, -1, 100],
)
@pytest.mark.asyncio
async def test_rate_movie_invalid_rating(
        client,
        movie_service,
        rating,
):
    application.dependency_overrides[get_movie_service] = (
        lambda: movie_service
    )

    response = await client.post(
        "/api/v1/movies/1/rate",
        params={"user_rating": rating},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Rating must be between 1 and 10"
    )

    movie_service.rate_movie.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_comment(
        client,
        movie_service,
        comment_service,
):
    application.dependency_overrides[get_movie_service] = (
        lambda: movie_service
    )

    application.dependency_overrides[get_comment_service] = (
        lambda: comment_service
    )

    comment_service.create_comment.return_value = {
        "id": 1,
        "user_id": 1,
        "text": "Great movie!",
    }

    response = await client.post(
        "/api/v1/movies/1/leave_comment",
        json={"text": "Great movie!"},
    )

    assert response.status_code == 200
    assert response.json()["text"] == "Great movie!"

    comment_service.create_comment.assert_awaited_once()
