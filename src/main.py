from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from routes import (
    movie_router,
    accounts_router,
    profiles_router,
    genre_router,
    star_router,
    director_router,
    certification_router,
)

app = FastAPI(
    title="Online Cinema",
)

api_version_prefix = "/api/v1"

app.include_router(
    accounts_router, prefix=f"{api_version_prefix}/accounts", tags=["accounts"]
)
app.include_router(
    profiles_router, prefix=f"{api_version_prefix}/profiles", tags=["profiles"]
)
app.include_router(movie_router, prefix=f"{api_version_prefix}/movies", tags=["movies"])
app.include_router(genre_router, prefix=f"{api_version_prefix}/genres", tags=["genres"])
app.include_router(star_router, prefix=f"{api_version_prefix}/stars", tags=["stars"])
app.include_router(
    director_router, prefix=f"{api_version_prefix}/directors", tags=["directors"]
)
app.include_router(
    certification_router,
    prefix=f"{api_version_prefix}/certifications",
    tags=["certifications"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
):
    errors = []

    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )
