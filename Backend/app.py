from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from routers.auth import auth_router
from typing import AsyncGenerator
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware

class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()

# Initialize the database engine and session
engine = create_async_engine(settings.DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs. Use a specific list of origins in production.
    allow_credentials=True,
    allow_methods=["*"],  # Adjust this to the allowed methods
    allow_headers=["*"],  # Adjust this to the allowed headers
)

# Include the router from auth.py
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# Dependency to get the database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

# Optionally, you can add event handlers for startup and shutdown
@app.on_event("startup")
async def on_startup():
    # Connect to the database or perform other startup tasks
    pass

@app.on_event("shutdown")
async def on_shutdown():
    # Disconnect from the database or perform other shutdown tasks
    await engine.dispose()
