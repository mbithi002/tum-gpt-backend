from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Message
from schemas import UserCreate, UserOut, UserLogin, TokenData, UserUpdate, UserResponse, MessageOut, MessageCreate
from auth import hash_password, create_access_token, verify_password
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import os
from uuid import UUID  # For UUID validation
import shortuuid

router = APIRouter(prefix="/users", tags=["Users"])

SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# ------------------- Helper Functions -------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Verify JWT token and return the user (UUID-compatible)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user
    except jwt.PyJWTError:
        raise credentials_exception

# ------------------- User Routes -------------------
@router.get("/", response_model=list[UserResponse])
async def read_users(limit: int = 25, offset: int = 0, db: Session = Depends(get_db)):
    """Return all users with pagination (now UUID-based)"""
    users = db.query(User).offset(offset).limit(limit).all()
    return users

@router.get("/user/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: UUID, db: Session = Depends(get_db)):
    """Return user by UUID"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.delete("/delete-by-id/{user_id}")
def delete_user_by_id(user_id: UUID, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (auto-generates UUID)"""
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = hash_password(user.password)
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token (unchanged, uses email)"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": db_user.email}, expires_delta=timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def get_user_session(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/update", response_model=UserOut)
def update_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user details (UUID-compatible)"""
    if user_update.username:
        current_user.username = user_update.username
    if user_update.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = user_update.email
    db.commit()
    db.refresh(current_user)
    return current_user

# ------------------- Message Routes -------------------
@router.post("/messages/send", response_model=MessageOut)
def send_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message (uses UUID for sender_id and shortuuid for collection)"""
    new_message = Message(
        sender_id=current_user.id,
        message=message.message,
        collection=message.collection or shortuuid.uuid()
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

@router.get("/messages/{collection}", response_model=list[MessageOut])
def get_messages_by_collection(
    collection: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all messages in a collection (shortuuid-based)"""
    messages = db.query(Message).filter(
        Message.collection == collection,
        Message.sender_id == current_user.id
    ).all()
    return messages