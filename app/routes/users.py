from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserOut, UserLogin, TokenData, UserUpdate, UserResponse
from auth import hash_password, create_access_token, verify_password
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import os

router = APIRouter(prefix="/users", tags=["Users"])

SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Verify JWT token and return the user"""
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

@router.get("/", response_model=list[UserResponse])
async def read_users(
    limit: int = 25, 
    offset: int = 0,  # Fixed offset default value
    db: Session = Depends(get_db)
):
    """Return all users with pagination"""
    users = db.query(User).offset(offset).limit(limit).all()
    return users

@router.get("/user/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """Return user by id"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": db_user.email}, expires_delta=timedelta(minutes=30))
    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserOut)
def get_user_session(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout():
    """Sign out (Client-side should clear token)"""
    return {"message": "User logged out. Please remove token from client-side."}


@router.put("/update", response_model=UserOut)
def update_user(user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update user details"""
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


@router.post("/recover-password")
def recover_password(email: str, db: Session = Depends(get_db)):
    """Send a password reset link (Simulated here)"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Simulated password reset link
    reset_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(hours=1))
    return {"message": "Password reset link sent", "reset_token": reset_token}


@router.delete("/delete-account")
def delete_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete user account"""
    db.delete(current_user)
    db.commit()
    return {"message": "User account deleted successfully"}
