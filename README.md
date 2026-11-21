# Online Cinema API

A RESTful API for an online cinema platform built with FastAPI. The application provides functionality for user account management, authentication, movie management, file storage, and email notifications.

## Technologies

- **Python 3.12+** — programming language
- **FastAPI** — REST API framework
- **PostgreSQL** — relational database
- **SQLAlchemy** — ORM
- **Alembic** — database migrations
- **Poetry** — dependency management
- **Docker & Docker Compose** — containerization
- **JWT** — authentication and authorization
- **MinIO / S3** — object storage
- **MailHog** — email testing
- **Pytest** — automated testing

## Features

### Authentication and Accounts
- User registration.
- JWT-based authentication.
- Secure password hashing.
- Email verification.
- Password recovery.
- Email notifications.

### User Profiles
- User profile management.
- Input data validation.

### Movies
- Movie management.
- Genre management.
- Director management.
- Actor management.
- Movie certification management.
- Comment management.

### File Storage
- MinIO and S3 integration.
- File uploading and storage.
- Separate storage service implementation.

### Testing
- Unit tests.
- Integration tests.
- End-to-end tests.
- Dependency overrides and test fixtures.

## Installation and Setup

### Prerequisites

Make sure you have the following tools installed:

- Python 3.12+
- Poetry
- Docker
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/pavliukkk/online-cinema.git
cd online-cinema
```

### 2. Configure environment variables

Create a `.env` file in the project root directory (can copy from .env.sample).

Configure the required environment variables according to the application settings.

Do not commit sensitive information such as passwords, secret keys, or credentials to the repository.

### 3. Install dependencies

```bash
poetry install
```

### 4. Start the application

Build and start the Docker containers:

```bash
docker compose up --build -d
```

To view application logs:

```bash
docker compose logs -f
```

To stop the containers:

```bash
docker compose down
```

## Database Migrations

The project uses Alembic to manage database schema changes.

Create a new migration:

```bash
poetry run alembic revision --autogenerate -m "Migration description"
```

Apply migrations:

```bash
poetry run alembic upgrade head
```

Run migrations inside the Docker container:

```bash
docker compose exec web poetry run alembic upgrade head
```

## API Documentation

Once the application is running, interactive API documentation is available at:

| Documentation | Endpoint |
|---|---|
| Swagger UI | `/docs` |
| ReDoc | `/redoc` |
| OpenAPI Schema | `/openapi.json` |

For a local instance:

```text
http://localhost:8000/docs
http://localhost:8000/redoc
```

## Testing

Run the test suite:

```bash
poetry run pytest
```

Run the tests e2e:

```bash
docker compose -f docker-compose-tests.yml down
docker compose -f docker-compose-tests.yml up --build --abort-on-container-exit --exit-code-from web
```

Run tests with verbose output:

```bash
poetry run pytest -v
```

Run tests with code coverage (if `pytest-cov` is installed):

```bash
poetry run pytest --cov=src
```

## Code Quality

Check code style using Flake8:

```bash
poetry run flake8 src/
```

## Local Development

Navigate to the src directory:

```bash
cd src
```

Start the development server:

```bash
uvicorn src.main:app --reload
```

The `--reload` option automatically restarts the server when source files change.

## Email Notifications

The application includes email notification functionality for account-related operations.

MailHog is provided for testing email delivery in the development environment.

## Object Storage

The application supports MinIO, an object storage solution compatible with the Amazon S3 API.

Storage-related functionality is implemented in the `src/storages/` module.

## License

This project is intended for educational and development purposes.