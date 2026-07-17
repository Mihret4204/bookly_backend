import uuid
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.books.schemas import BookSchema, BookCreateSchema, BookUpdateSchema, BookDetailSchema
from src.books.service import BookService
from src.db.main import get_session

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])


@book_router.get("/", response_model=List[BookSchema])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    return await book_service.get_all_books(session)


@book_router.get(
    "/user/{user_uid}/",
    response_model=List[BookSchema],
    dependencies=[Depends(role_checker)],
)
async def get_user_books(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    return await book_service.get_user_books(user_uid, session)


@book_router.post(
    "/create_book",
    status_code=status.HTTP_201_CREATED,
    response_model=BookSchema,
)
async def create_book(
    book_data: BookCreateSchema,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    user_id = token_details.get("user")["user_uid"]
    return await book_service.create_book(book_data, user_id, session)


@book_router.get(
    "/{book_uid}/",
    response_model=BookDetailSchema,
    dependencies=[Depends(role_checker)],
)
async def get_book(
    book_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    book = await book_service.get_book(book_uid, session)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@book_router.patch(
    "/update_book/{book_uid}/",
    response_model=BookSchema,
    dependencies=[Depends(role_checker)],
)
async def update_book(
    book_uid: uuid.UUID,
    book_data: BookUpdateSchema,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    updated = await book_service.update_book(book_uid, book_data, session)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return updated


@book_router.delete(
    "/delete_book/{book_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_checker)],
)
async def delete_book(
    book_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    deleted = await book_service.delete_book(book_uid, session)
    if deleted is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return None


@book_router.post(
    "/{book_uid}/cover",
    status_code=status.HTTP_201_CREATED,
    response_model=BookSchema,
    dependencies=[Depends(role_checker)],
)
async def add_book_cover(
    book_uid: uuid.UUID,
    cover: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    if not (cover.content_type or "").startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cover must be an image file"
        )
    user_id = uuid.UUID(token_details.get("user")["user_uid"])
    updated = await book_service.add_or_replace_book_cover(book_uid, user_id, cover, session)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return updated


@book_router.delete(
    "/{book_uid}/cover",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_checker)],
)
async def remove_book_cover(
    book_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    user_id = uuid.UUID(token_details.get("user")["user_uid"])
    updated = await book_service.remove_book_cover(book_uid, user_id, session)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return None
