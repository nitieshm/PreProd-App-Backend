# Backend/schemas.py

from pydantic import BaseModel

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
