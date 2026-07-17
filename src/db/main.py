import os
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from ..config import Settings
from sqlmodel import SQLModel
from src.db.models import Book


config = Settings()

environment_url = os.getenv('DATABASE_URL', config.DATABASE_URL)

async_engine: AsyncEngine = create_async_engine(
    environment_url,
    echo=True,
    connect_args={
    "statement_cache_size": 0
}
 
)

async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
            
        
async def get_session()->AsyncSession:

    Session = sessionmaker(
        bind=async_engine,
        class_ = AsyncSession,
        expire_on_commit=False
    )
    async with Session() as session:
        yield session