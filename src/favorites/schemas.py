import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class FavoriteBookSchema(BaseModel):
    """Book fields returned inside a favorites list."""
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
    cover_image_path: Optional[str] = None
    cover_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FavoriteResponseSchema(BaseModel):
    book_uid: uuid.UUID
    user_uid: uuid.UUID
    created_at: datetime


class UserFavoritesResponseSchema(BaseModel):
    favorites: List[FavoriteBookSchema]


# Backward-compat aliases
FavoriteBook = FavoriteBookSchema
FavoriteResponse = FavoriteResponseSchema
UserFavoritesResponse = UserFavoritesResponseSchema
