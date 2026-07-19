from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from src.config import Config
import jwt
import uuid
import logging
from itsdangerous import URLSafeSerializer

passwd_context = CryptContext(
    schemes=['bcrypt']
)
ACCESS_TOKEN_EXPIRY = 15 * 60

def generate_password_hash(password: str) -> str:
    hash = passwd_context.hash(password)
    return hash

def verify_password(password: str, hash: str) -> bool:
    return passwd_context.verify(password, hash)

def create_access_token(
    user_data: dict,
    expiry: Optional[timedelta] = None,
    refresh: bool = False,
    refresh_jti: Optional[str] = None,
):
    payload = {}

    payload['user'] = user_data
    payload['exp'] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh

    if refresh_jti is not None:
        payload['refresh_jti'] = refresh_jti
    elif refresh:
        payload['refresh_jti'] = payload['jti']

    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM
    )

    return token
def decode_token(token: str)->dict:

    try:
        token_data= jwt.decode(
            jwt=token,
            key= Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return  token_data
    except jwt.PyJWTError as jwte:
        logging.exception(jwte)
        return None
    except Exception as e:
        logging.exception(e)
        return None

serializer= URLSafeSerializer(
        secret_key=Config.JWT_SECRET_KEY,
        salt='email.configuration'
    )

def create_url_safe_token(data: dict):
    
    token= serializer.dumps(data)

    return token

def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(str(e))
        