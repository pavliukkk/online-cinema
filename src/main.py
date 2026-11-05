from fastapi import FastAPI

from routes import (
    movie_router,
    accounts_router,
)

app = FastAPI(
    title="Online Cinema",
)

api_version_prefix = "/api/v1"

app.include_router(accounts_router, prefix=f"{api_version_prefix}/accounts", tags=["accounts"])
app.include_router(movie_router, prefix=f"{api_version_prefix}/movies", tags=["movies"])