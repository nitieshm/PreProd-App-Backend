# Backend/database.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = ".env"


# Initialize settings and load the DATABASE_URL
settings = Settings()

# Extract the database URL from settings
DATABASE_URL = settings.database_url

# Create the async engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# Base class for the models
Base = declarative_base()

# Dependency for the database session
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
