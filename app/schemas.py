from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
import uuid  # For UUID validation
from pydantic.types import conint

# ------------------- User Schemas -------------------
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID  # Matches UUID from SQLAlchemy
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime
    last_login: datetime

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

# ------------------- Message Schemas -------------------
class MessageCreate(BaseModel):
    message: str
    collection: Optional[str] = None  # Let shortuuid generate it if not provided

class MessageOut(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID  # Matches User.id (UUID)
    message: str
    collection: str  # shortuuid string
    response: Optional[str] = None
    created_at: datetime  # Renamed from 'timestamp' to match model

    class Config:
        orm_mode = True

# ------------------- Auth Schemas -------------------
class TokenData(BaseModel):
    email: Optional[str] = None