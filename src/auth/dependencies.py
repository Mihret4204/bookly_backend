from fastapi import Request, status, Depends
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token
from fastapi.exceptions import HTTPException
from src.db.redis import token_in_blocklist
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .service import UserService
from typing import List, Any, Dict, Optional
from src.db.models import User

user_service = UserService()


class TokenBearer(HTTPBearer):
    """Base token bearer that extracts, decodes, and validates tokens."""
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Dict[str, Any]:
        """Intercepts the request, extracts the credentials, and validates the token."""
        # 1. Fetch credentials using HTTPBearer's native __call__
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(request)
        
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='No authorization credentials provided'
            )
            
        # 2. Extract token string safely
        token = credentials.credentials
        token_data = decode_token(token)
        
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid or expired token'
            )
            
        # 3. Check Redis Blocklist
        if await token_in_blocklist(token_data.get('jti', '')):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    'error': 'This token is invalid or has been revoked',
                    'resolution': 'Please get a new token'
                }
            )
            
        # 4. Enforce Token Type (Access vs Refresh)
        self.verify_token_data(token_data)
        
        return token_data
    
    def verify_token_data(self, token_data: Dict[str, Any]) -> None:
        """Override in subclass to add specific token type checks."""
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    """Bearer for access tokens - ensures token is not a refresh token."""
    
    def verify_token_data(self, token_data: Dict[str, Any]) -> None:
        if token_data and token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Please provide an access token'
            )


class RefreshTokenBearer(TokenBearer):
    """Bearer for refresh tokens - ensures token is a refresh token."""
    
    def verify_token_data(self, token_data: Dict[str, Any]) -> None:
        if token_data and not token_data.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Please provide a refresh token'
            )


# Instantiate the bearers to use directly as dependencies
get_access_token_data = AccessTokenBearer()
get_refresh_token_data = RefreshTokenBearer()


async def get_current_user(
    token_data: Dict[str, Any] = Depends(get_access_token_data),
    session: AsyncSession = Depends(get_session)
) -> User:
    """Get the current user from the access token."""
    user_info = token_data.get('user')
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token structure'
        )
    
    user_email = user_info.get('email')
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token: no email found'
        )
    
    user = await user_service.get_user_by_email(user_email, session)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    
    return user


class RoleChecker:
    """Dependency to check if user has required role."""
    
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> bool:
        return True
