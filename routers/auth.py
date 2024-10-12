from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User  # Use absolute import
from database import get_db  # Use absolute import
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer

auth_router = APIRouter()

# Hashing and JWT setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
SECRET_KEY = "Admin*123"  # Secure this
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Models
class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str
    role: str
    email: str
    mobile_number: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    username: str

# Utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_user_by_username(username: str, db: AsyncSession):
    result = await db.execute(select(User).filter_by(username=username))
    return result.scalars().first()

# Routes
@auth_router.post("/register")
async def register_user(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Check if username already exists
    existing_user = await get_user_by_username(request.username, db)
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

@auth_router.post("/login")
async def login_user(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(request.username, db)

    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Generate JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role  # Include the user role in the response
    }

@auth_router.get("/get-user-role")
async def get_user_role(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await get_user_by_username(username, db)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"role": user.role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
