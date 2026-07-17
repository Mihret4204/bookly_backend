import os
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

from src.reviews.schemas import ReviewModel


# ──────────────────────────────────────────────────────────────
# Nested creator sub-schema (safe subset of User)
# ──────────────────────────────────────────────────────────────

class BookCreatorSchema(BaseModel):
    uid: uuid.UUID
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────────────────────
# Book response schema
# ──────────────────────────────────────────────────────────────

class BookSchema(BaseModel):
    """Response schema for a single book. Maps ORM → API."""

    book_uid: uuid.UUID = Field(alias="uid")
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str
    cover_image_path: Optional[str] = None
    cover_url: Optional[str] = None
    user_uid: Optional[uuid.UUID] = None
    creator: Optional[BookCreatorSchema] = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def compute_cover_url(self) -> "BookSchema":
        if self.cover_image_path and not self.cover_url:
            if self.cover_image_path.startswith(("http://", "https://")):
                self.cover_url = self.cover_image_path
            else:
                filename = os.path.basename(self.cover_image_path)
                self.cover_url = (
                    f"http://127.0.0.1:8000/uploads/covers/books/{filename}"
                )
        return self

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }

class BookDetailSchema(BookSchema):
    """Book response with full reviews list."""
    reviews: List[ReviewModel] = []


# ──────────────────────────────────────────────────────────────
# Request schemas
# ──────────────────────────────────────────────────────────────

class BookCreateSchema(BaseModel):
    """Input schema for creating a book."""
    title: str
    author: str
    publisher: str
    published_date: str = Field(
        description="Date as a string, e.g. '2024-01-15'"
    )
    page_count: int = Field(gt=0)
    language: str


class BookUpdateSchema(BaseModel):
    """Input schema for updating a book (all fields required for a full update)."""
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int = Field(gt=0)
    language: str


# ──────────────────────────────────────────────────────────────
# Backward-compat aliases so existing imports don't break
# ──────────────────────────────────────────────────────────────
Book = BookSchema
BookDetailModel = BookDetailSchema
BookCreateModel = BookCreateSchema
updateBookModel = BookUpdateSchema
