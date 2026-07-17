from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.utils import (
    create_access_token,
    create_url_safe_token,
    decode_url_safe_token,
    generate_password_hash,
    verify_password,
)
from src.celery_tasks import send_email
from src.config import Config
from src.db.main import get_session
from src.db.models import Book, User, UserFavorite
from src.db.redis import add_jti_to_blocklist
from src.mail import create_message, mail

from .dependencies import (
    RoleChecker,
    get_access_token_data,
    get_current_user,
    get_refresh_token_data,
)
from .schemas import (
    EmailModel,
    PasswordResetConfirmModel,
    PasswordResetRequestModel,
    UserCreateModel,
    UserLoginModel,
    UserSchema,
)
from .service import UserService

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = 2


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    send_email.delay(emails.addresses, "Welcome to the app", "<h1>Welcome to the app</h1>")
    return {"message": "Email sent successfully"}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateModel,
    bg_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    email = user_data.email
    if await user_service.user_exists(email, session):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A user with that email already exists.",
        )

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"
    html = f'<h1>Verify your Email</h1><a href="{link}">Click to verify your email.</a>'
    send_email.delay([email], "Verify your email", html)

    return {
        "message": "Account created. Please verify your email.",
        "user": UserSchema.model_validate(new_user),
    }


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")

    if not user_email:
        return JSONResponse(
            content={"message": "Invalid verification token"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await user_service.update_user(user, {"is_verified": True}, session)
    return JSONResponse(
        content={"message": "Account verified successfully"},
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/login")
async def login(
    login_data: UserLoginModel,
    session: AsyncSession = Depends(get_session),
):
    user = await user_service.get_user_by_email(login_data.email, session)

    if user and verify_password(login_data.password, user.password_hash):
        access_token = create_access_token(
            user_data={
                "email": user.email,
                "user_uid": str(user.uid),
                "role": str(user.role),
            }
        )
        refresh_token = create_access_token(
            user_data={"email": user.email, "user_uid": str(user.uid)},
            refresh=True,
            expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
        )
        return JSONResponse(
            content={
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "email": user.email,
                    "uid": str(user.uid),
                    "user_uid": str(user.uid),
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                },
            }
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid email or password",
    )


@auth_router.get("/refresh_token")
async def get_new_access_token(
    token_data: Dict[str, Any] = Depends(get_refresh_token_data),
):
    expiry_timestamp = token_data["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_data["user"])
        return JSONResponse(content={"access_token": new_access_token})
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
    )


@auth_router.get("/me")
async def get_me(
    user: User = Depends(get_current_user),
    _: bool = Depends(role_checker),
    session: AsyncSession = Depends(get_session),
):
    """Return the authenticated user's profile with their books and favorites count."""
    books_result = await session.execute(
        select(Book)
        .where(Book.user_uid == user.uid)
        .order_by(desc(Book.created_at))
    )
    books_created = list(books_result.scalars().all())

    fav_result = await session.execute(
        select(UserFavorite).where(UserFavorite.user_uid == user.uid)
    )
    favorites_count = len(list(fav_result.scalars().all()))

    return {
        "uid": str(user.uid),
        "user_uid": str(user.uid),
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "profile_image": user.profile_image,
        "role": user.role,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        "_favorites_count": favorites_count,
        "books": [
            {
                "book_uid": str(b.uid),
                "uid": str(b.uid),
                "title": b.title,
                "author": b.author,
                "publisher": b.publisher,
                "published_date": b.published_date,
                "page_count": b.page_count,
                "language": b.language,
                "cover_image_path": b.cover_image_path,
                "created_at": b.created_at.isoformat() if b.created_at else None,
                "updated_at": b.updated_at.isoformat() if b.updated_at else None,
            }
            for b in books_created
        ],
    }


@auth_router.get("/logout")
async def revoke_token(
    token_data: Dict[str, Any] = Depends(get_access_token_data),
):
    jti = token_data["jti"]
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={"message": "Logged out successfully"},
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email
    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    html_message = f'<h1>Reset Your Password</h1><p><a href="{link}">Click here</a> to reset your password.</p>'
    message = create_message(recipients=[email], subject="Reset your password", body=html_message)
    await mail.send_message(message)
    return JSONResponse(
        content={"message": "Please check your email for password reset instructions"},
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    if passwords.new_password != passwords.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
        )

    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")

    if not user_email:
        return JSONResponse(
            content={"message": "Invalid password reset token"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    passwd_hash = generate_password_hash(passwords.new_password)
    await user_service.update_user(user, {"password_hash": passwd_hash}, session)

    return JSONResponse(
        content={"message": "Password reset successfully"},
        status_code=status.HTTP_200_OK,
    )
