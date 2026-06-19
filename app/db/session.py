# app/db/session.py
from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

# engine - manages the connection pool 
# echo = true prints every sql query to terminal during development - invaluable for debugging.
# set to false in production
engine = create_async_engine(settings.database_url, echo=True)

# sessionmaker creates a session factory.
# class when called produces a new session object with your chosen config.
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# FastAPI dependency using Python's generator pattern.
async def get_db():
    # async with - guarantees cleanup runs if an exception is thrown.
    # creates a new session
    async with AsyncSessionLocal() as session:
        try:
            # transforms function into a generator
            # FastAPI's dependency injection system understands those.
            yield session
        finally:
            await session.close()