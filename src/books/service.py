import os
import uuid
from datetime import date

from fastapi import UploadFile
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.schemas import BookCreateSchema, BookUpdateSchema
from src.db.models import Book
from src.supabase_client import supabase_storage_client


class BookService:

    async def get_all_books(self, session: AsyncSession) -> list[Book]:
        statement = (
            select(Book)
            .options(
                selectinload(Book.reviews),
                selectinload(Book.tags),
                joinedload(Book.user),
            )
            .order_by(Book.created_at.desc())
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    # backward-compat alias used by existing routes
    async def get_all_book(self, session: AsyncSession) -> list[Book]:
        return await self.get_all_books(session)

    async def get_user_books(self, user_uid: str, session: AsyncSession) -> list[Book]:
        statement = (
            select(Book)
            .where(Book.user_uid == uuid.UUID(user_uid))
            .order_by(desc(Book.created_at))
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    async def get_book(self, book_uid: uuid.UUID, session: AsyncSession) -> Book | None:
        statement = (
            select(Book)
            .where(Book.uid == book_uid)
            .options(
                selectinload(Book.reviews),
                selectinload(Book.tags),
                joinedload(Book.user),
            )
        )
        result = await session.execute(statement)
        return result.scalars().first()

    async def create_book(
        self,
        book_data: BookCreateSchema,
        user_uid: str,
        session: AsyncSession,
    ) -> Book:
        data = book_data.model_dump()

        # Normalise published_date: always store as ISO string in VARCHAR column
        raw_date = data.get("published_date")
        if isinstance(raw_date, date):
            data["published_date"] = raw_date.isoformat()

        new_book = Book(**data)
        new_book.user_uid = uuid.UUID(user_uid)
        new_book.uid = uuid.uuid4()

        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        return new_book

    async def search_books(self, query: str, session: AsyncSession) -> list[Book]:
        statement = (
            select(Book)
            .where(
                Book.title.ilike(f"%{query}%")
                | Book.author.ilike(f"%{query}%")
            )
            .order_by(desc(Book.created_at))
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    async def update_book(
        self,
        book_uid: uuid.UUID,
        update_data: BookUpdateSchema,
        session: AsyncSession,
    ) -> Book | None:
        book = await self.get_book(book_uid, session)
        if book is None:
            return None

        for key, value in update_data.model_dump().items():
            # Normalise date fields on the way in
            if key == "published_date" and isinstance(value, date):
                value = value.isoformat()
            setattr(book, key, value)

        await session.commit()
        await session.refresh(book)
        return book

    async def delete_book(
        self, book_uid: uuid.UUID, session: AsyncSession
    ) -> Book | None:
        """Hard-delete the book row and its cover file."""
        book = await self.get_book(book_uid, session)
        if book is None:
            return None

        if book.cover_image_path:
            try:
                await supabase_storage_client.delete_file(book.cover_image_path)
            except Exception:
                pass

        await session.delete(book)
        await session.commit()
        return book

    # ── Cover helpers ────────────────────────────────────────────

    async def add_or_replace_book_cover(
        self,
        book_uid: uuid.UUID,
        user_uid: uuid.UUID,
        cover_file: UploadFile,
        session: AsyncSession,
    ) -> Book | None:
        book = await self.get_book(book_uid, session)
        if book is None:
            return None

        if book.cover_image_path:
            try:
                await supabase_storage_client.delete_file(book.cover_image_path)
            except Exception:
                pass

        content = await cover_file.read()
        public_url = await supabase_storage_client.upload_file(
            file_bytes=content,
            filename=cover_file.filename or "cover",
            content_type=cover_file.content_type or "image/jpeg",
            book_uid=book_uid,
        )

        book.cover_image_path = public_url
        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book

    async def remove_book_cover(
        self,
        book_uid: uuid.UUID,
        user_uid: uuid.UUID,
        session: AsyncSession,
    ) -> Book | None:
        book = await self.get_book(book_uid, session)
        if book is None:
            return None

        if book.cover_image_path:
            try:
                await supabase_storage_client.delete_file(book.cover_image_path)
            except Exception:
                pass

        book.cover_image_path = None
        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book
