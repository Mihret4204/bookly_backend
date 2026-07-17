import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.books.schemas import BookSchema
from src.reviews.schemas import ReviewModel


# ──────────────────────────────────────────────────────────────
# Auth request schemas
# ──────────────────────────────────────────────────────────────

class UserCreateModel(BaseModel):
    username: str = Field(max_length=32)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6, max_length=128)
    first_name: Optional[str] = Field(default=None, max_length=25)
    last_name: Optional[str] = Field(default=None, max_length=25)


class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=1, max_length=128)  # fixed: was max_length=12


# ──────────────────────────────────────────────────────────────
# User response schemas
# ──────────────────────────────────────────────────────────────

class UserSchema(BaseModel):
    """Safe user response — never exposes password_hash."""
    uid: uuid.UUID
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image: Optional[str] = None
    role: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class UserProfileSchema(UserSchema):
    """Extended user response used for /me — includes books, reviews, counts."""
    books: List[BookSchema] = []
    reviews: List[ReviewModel] = []
    _favorites_count: int = 0

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


# ──────────────────────────────────────────────────────────────
# Misc
# ──────────────────────────────────────────────────────────────

class EmailModel(BaseModel):
    addresses: List[str]


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str


# ──────────────────────────────────────────────────────────────
# Backward-compat aliases
# ──────────────────────────────────────────────────────────────
UserModel = UserSchema
UserBooksModel = UserProfileSchema
