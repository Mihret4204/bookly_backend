# inside src/config.py

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    REDIS_URL: str | None = None
    ENABLE_CELERY: bool = False
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DOMAIN: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings():
    return Settings()


Config = get_settings()

if Config.ENABLE_CELERY and Config.REDIS_URL:
    broker_url = Config.REDIS_URL
    result_backend = Config.REDIS_URL
else:
    broker_url = "memory://"
    result_backend = "cache+memory://"

broker_connection_retry_on_startup = True