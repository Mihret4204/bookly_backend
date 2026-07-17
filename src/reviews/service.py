import logging

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.service import UserService
from src.books.service import BookService
from src.db.models import Review

from .schemas import ReviewCreateModel

book_service = BookService()
user_service = UserService()


class ReviewService:

    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ) -> Review:
        try:
            book = await book_service.get_book(book_uid=book_uid, session=session)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
                )

            user = await user_service.get_user_by_email(email=user_email, session=session)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            new_review = Review(**review_data.model_dump())
            new_review.user = user
            new_review.book = book

            session.add(new_review)
            await session.commit()
            await session.refresh(new_review)
            return new_review

        except HTTPException:
            raise
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred",
            )

    async def get_review(self, review_uid: str, session: AsyncSession) -> Review | None:
        statement = select(Review).where(Review.uid == review_uid)
        result = await session.execute(statement)
        return result.scalars().first()

    async def get_all_reviews(self, session: AsyncSession) -> list[Review]:
        statement = select(Review).order_by(desc(Review.created_at))
        result = await session.execute(statement)
        return list(result.scalars().all())

    async def delete_review(
        self, review_uid: str, user_email: str, session: AsyncSession
    ) -> None:
        user = await user_service.get_user_by_email(user_email, session)
        review = await self.get_review(review_uid, session)

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
            )

        if review.user_uid != user.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews",
            )

        await session.delete(review)
        await session.commit()
