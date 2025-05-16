from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create async engine for the database
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Ensures the connection is still active
    echo=settings.DEBUG,  # Print SQL queries in debug mode
)

# Create sessionmaker
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields DB sessions
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise 