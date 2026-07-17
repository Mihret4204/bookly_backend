import uuid
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import status
from fastapi.exceptions import HTTPException

from src.db.models import UserFavorite, Book, User


class FavoriteService:

    async def get_user_favorites(self, user: User, session: AsyncSession):
        """Return all books the user has favorited."""
        statement = (
            select(Book)
            .join(UserFavorite, UserFavorite.book_uid == Book.uid)   # FIXED: matches Book.uid
            .where(UserFavorite.user_uid == user.uid)               # FIXED: matches user.uid
        )
        result = await session.execute(statement)
        return result.scalars().all()

    async def add_favorite(
        self, book_uid: uuid.UUID, user: User, session: AsyncSession
    ) -> UserFavorite:
        """Add a book to the user's favorites. 409 if already favorited."""
        # verify book exists
        book_result = await session.execute(
            select(Book).where(Book.uid == book_uid)                # FIXED: matches Book.uid
        )
        book = book_result.scalars().first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )

        # check duplicate
        existing = await session.execute(
            select(UserFavorite).where(
                UserFavorite.user_uid == user.uid,                  # FIXED: matches user.uid
                UserFavorite.book_uid == book_uid,
            )
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Book is already in favorites",
            )

        favorite = UserFavorite(user_uid=user.uid, book_uid=book_uid) # FIXED: matches user.uid
        session.add(favorite)
        await session.commit()
        await session.refresh(favorite)
        return favorite

    async def remove_favorite(
        self, book_uid: uuid.UUID, user: User, session: AsyncSession
    ) -> None:
        """Remove a book from the user's favorites. 404 if not present."""
        result = await session.execute(
            select(UserFavorite).where(
                UserFavorite.user_uid == user.uid,                  # FIXED: matches user.uid
                UserFavorite.book_uid == book_uid,
            )
        )
        favorite = result.scalars().first()
        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found in favorites",
            )
        await session.delete(favorite)
        await session.commit()