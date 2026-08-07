from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)

class AuthUser(BaseModel):
    id: str
    email: str
    name: str

class AuthTokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser

class AuthResponse(BaseModel):
    user: AuthUser
    access_token: Optional[str] = None
