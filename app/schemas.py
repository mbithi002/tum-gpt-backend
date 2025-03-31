from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin (BaseModel):
    email: EmailStr
    password: str
    
class UserResponse (BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime
    updated_at: datetime
    last_login: datetime
    class Config:
        orm_mode = True

# class UserOut(BaseModel):
#     id: int
#     email: str
#     username: str
#     created_at: datetime

#     class Config:
#         orm_mode = True

class MessageCreate(BaseModel):
    message: str
    # collection: int

class MessageOut(BaseModel):
    id: int
    sender_id: int
    message: str
    # collection: int
    response: Optional[str]
    timestamp: datetime

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None

class TokenData(BaseModel):
    email: Optional[str] = None
