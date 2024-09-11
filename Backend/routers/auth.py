# Backend/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User  # Use absolute import
from database import get_db  # Use absolute import

auth_router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str
    role: str
    email: str
    mobile_number: str

@auth_router.post("/register")
async def register_user(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Check if username already exists
    result = await db.execute(select(User).filter_by(username=request.username))
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Create and add new user to the database
    new_user = User(
        username=request.username,
        password=hash_password(request.password),  # Store hashed password
        role=request.role,
        email=request.email,
        mobile_number=request.mobile_number
    )
    
    db.add(new_user)
    await db.commit()
    
    return {"message": "User registered successfully"}

class LoginRequest(BaseModel):
    username: str
    password: str

@auth_router.post("/login")
async def login_user(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter_by(username=request.username))
    user = result.scalars().first()
    
    if not user or not verify_password(user.password, request.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    return {"message": "Login successful"}

def hash_password(password: str) -> str:
    # Implement password hashing logic here
    return password  # Replace with actual hashed password

def verify_password(stored_password: str, provided_password: str) -> bool:
    # Implement password verification logic here
    return stored_password == provided_password  # Replace with actual verification
