from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BaseResponseSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class BaseCreateSchema(BaseModel):
    name: str


class CommentResponseSchema(BaseModel):
    id: int
    user_id: int
    text: str

    model_config = {"from_attributes": True}


class CommentCreateSchema(BaseModel):
    text: str


class MovieSchema(BaseModel):
    id: int
    name: str
    uuid: UUID
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: Optional[float] = None
    gross: Optional[float] = None
    description: str
    price: Decimal
    genres: list[BaseResponseSchema]
    stars: list[BaseResponseSchema]
    directors: list[BaseResponseSchema]
    certification: BaseResponseSchema
    likes: Optional[int] = None
    dislikes: Optional[int] = None
    rate: Optional[float] = None
    rate_count: Optional[int] = None
    comments: Optional[list[CommentResponseSchema]] = None

    model_config = {"from_attributes": True}


class MovieCreateSchema(BaseCreateSchema):
    year: int = Field(ge=1888, le=2100)
    time: int = Field(gt=0)
    imdb: float = Field(ge=0, le=10)
    votes: int = Field(ge=0)

    meta_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )
    gross: Optional[float] = Field(default=None, ge=0)

    description: str
    price: Decimal = Field(gt=0)

    genres: list[int] = Field(min_length=1)
    stars: list[int] = Field(min_length=1)
    directors: list[int] = Field(min_length=1)

    certification_id: int = Field(gt=0)


class PaginatedMoviesResponse(BaseModel):
    movies: list[MovieSchema]
    prev_page: Optional[str]
    next_page: Optional[str]
    total_pages: int
    total_items: int
