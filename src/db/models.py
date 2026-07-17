from datetime import datetime
from typing import List, Optional
import uuid
import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Relationship


# ──────────────────────────────────────────────────────────────
# LINK / JUNCTION TABLES
# ──────────────────────────────────────────────────────────────

class BookTag(SQLModel, table=True):
    __tablename__ = "book_tags"

    book_uid: uuid.UUID = Field(
        foreign_key="books.uid",
        primary_key=True,
        ondelete="CASCADE",
    )
    tag_uid: uuid.UUID = Field(
        foreign_key="tags.uid",
        primary_key=True,
        ondelete="CASCADE",
    )


class UserFavorite(SQLModel, table=True):
    __tablename__ = "user_favorites"

    user_uid: uuid.UUID = Field(
        foreign_key="users.uid",
        primary_key=True,
        ondelete="CASCADE",
    )
    book_uid: uuid.UUID = Field(
        foreign_key="books.uid",
        primary_key=True,
        ondelete="CASCADE",
    )
    created_at: datetime = Field(default_factory=datetime.now)


# ──────────────────────────────────────────────────────────────
# USER
# ──────────────────────────────────────────────────────────────

class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.UUID,
            primary_key=True,
            unique=True,
            nullable=False,
            default=uuid.uuid4,
        )
    )
    username: str = Field(max_length=32, unique=True, nullable=False)
    email: str = Field(max_length=40, unique=True, nullable=False)
    first_name: Optional[str] = Field(max_length=25, default=None)
    last_name: Optional[str] = Field(max_length=25, default=None)
    role: str = Field(default="user", nullable=False)
    is_verified: bool = Field(default=False, nullable=False)
    password_hash: str = Field(nullable=False)
    profile_image: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.now},
    )

    # Relationships
    books: List["Book"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    reviews: List["Review"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    favorites: List["Book"] = Relationship(
        back_populates="favorited_by",
        link_model=UserFavorite,
    )


# ──────────────────────────────────────────────────────────────
# BOOK
# ──────────────────────────────────────────────────────────────

class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.UUID,
            primary_key=True,
            unique=True,
            nullable=False,
            default=uuid.uuid4,
        )
    )
    title: str = Field(nullable=False)
    author: str = Field(nullable=False)
    publisher: str = Field(nullable=False)
    # stored as VARCHAR — always convert date → str before persisting
    published_date: str = Field(nullable=False)
    page_count: int = Field(nullable=False)
    language: str = Field(nullable=False)
    cover_image_path: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.now},
    )

    # FK → users (nullable so book survives user deletion)
    user_uid: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="users.uid",
        ondelete="SET NULL",
    )

    # Relationships
    user: Optional[User] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(
        back_populates="book",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    tags: List["Tag"] = Relationship(
        back_populates="books",
        link_model=BookTag,
    )
    favorited_by: List[User] = Relationship(
        back_populates="favorites",
        link_model=UserFavorite,
    )

    def __repr__(self) -> str:
        return f"<Book {self.title!r}>"


# ──────────────────────────────────────────────────────────────
# REVIEW
# ──────────────────────────────────────────────────────────────

class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    uid: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.UUID,
            primary_key=True,
            unique=True,
            nullable=False,
            default=uuid.uuid4,
        )
    )
    rating: int = Field(nullable=False)
    review_text: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.now},
    )

    # FKs (nullable — reviews survive book/user soft-deletes)
    user_uid: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="users.uid",
        ondelete="CASCADE",
    )
    book_uid: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="books.uid",
        ondelete="CASCADE",
    )

    # Relationships
    user: Optional[User] = Relationship(back_populates="reviews")
    book: Optional[Book] = Relationship(back_populates="reviews")


# ──────────────────────────────────────────────────────────────
# TAG
# ──────────────────────────────────────────────────────────────

class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    uid: uuid.UUID = Field(
        sa_column=sa.Column(
            sa.UUID,
            primary_key=True,
            unique=True,
            nullable=False,
            default=uuid.uuid4,
        )
    )
    name: str = Field(max_length=30, unique=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)

    books: List[Book] = Relationship(
        back_populates="tags",
        link_model=BookTag,
    )
