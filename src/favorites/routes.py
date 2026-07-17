import uuid
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker, get_current_user
from src.db.main import get_session
from src.db.models import User

from .schemas import FavoriteResponse, UserFavoritesResponse, FavoriteBook
from .service import FavoriteService

favorites_router = APIRouter()
favorite_service = FavoriteService()
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@favorites_router.get(
    "/",
    response_model=UserFavoritesResponse,
    dependencies=[user_role_checker],
)
async def get_favorites(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    books = await favorite_service.get_user_favorites(current_user, session)
    return UserFavoritesResponse(favorites=[FavoriteBook.model_validate(b, from_attributes=True) for b in books])


@favorites_router.post(
    "/{book_uid}",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[user_role_checker],
)
async def add_favorite(
    book_uid: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    favorite = await favorite_service.add_favorite(book_uid, current_user, session)
    return FavoriteResponse(
        book_uid=favorite.book_uid,
        user_uid=favorite.user_uid,
        created_at=favorite.created_at,
    )


@favorites_router.delete(
    "/{book_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[user_role_checker],
)
async def remove_favorite(
    book_uid: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await favorite_service.remove_favorite(book_uid, current_user, session)
    return None