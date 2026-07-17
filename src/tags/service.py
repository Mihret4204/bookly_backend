from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.service import BookService
from src.db.models import Tag

from .schemas import TagAddModel, TagCreateModel

book_service = BookService()


server_error = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong"
)


class TagService:

    async def get_tags(self, session: AsyncSession):

        statement = select(Tag).order_by(desc(Tag.created_at))

        result = await session.execute(statement)

        return result.scalars().all()

    async def add_tags_to_book(self, book_uid: str, tag_data: TagCreateModel, session: AsyncSession):
        book = await book_service.get_book(book_uid=book_uid, session=session)

        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        result = await session.execute(
            select(Tag).where(Tag.name == tag_data.name))

        tag = result.scalar_one_or_none()

        if not tag:
            tag = Tag(name=tag_data.name)

        book.tags.append(tag)

        session.add(book)
        await session.commit()
        await session.refresh(book)

        return book


    async def get_tag_by_uid(self, tag_uid: str, session: AsyncSession):

        statement = select(Tag).where(Tag.uid == tag_uid)

        result = await session.execute(statement)

        return result.scalars().first()

    async def add_tag(self, tag_data: TagCreateModel, session: AsyncSession):
        """Create a tag"""

        statement = select(Tag).where(Tag.name == tag_data.name)

        result = await session.execute(statement)

        tag = result.scalar_one_or_none()

        if tag:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Tag exists"
            )

        new_tag = Tag(name=tag_data.name)

        session.add(new_tag)

        await session.commit()

        return new_tag

    async def update_tag(
        self, tag_uid, tag_update_data: TagCreateModel, session: AsyncSession
    ):

        tag = await self.get_tag_by_uid(tag_uid, session)

        update_data_dict = tag_update_data.model_dump()

        for k, v in update_data_dict.items():
            setattr(tag, k, v)

        await session.commit()

        await session.refresh(tag)

        return tag


    async def delete_tag(self, tag_uid: str, session: AsyncSession):
        tag = await self.get_tag_by_uid(tag_uid, session)

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag does not exist"
            )

        await session.delete(tag)

        await session.commit()