from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Message, User
from schemas import MessageCreate, MessageOut
from uuid import UUID
import shortuuid
from .users import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

# ------------------- Helper Functions -------------------
def verify_message_ownership(message: Message, current_user: User):
    """Check if the current user owns the message"""
    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this message"
        )

# ------------------- Chat Routes -------------------
@router.get("/", response_model=list[MessageOut])
def get_all_chats(
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all chats (admin-only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access all chats"
        )
    
    db_chats = db.query(Message).limit(limit).offset(offset).all()
    return db_chats

@router.get("/user/{user_id}", response_model=list[MessageOut])
def get_my_chats(
    user_id: UUID,
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chats for a specific user (must be owner or admin)"""
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only access your own chats"
        )

    db_chats = (
        db.query(Message)
        .filter(Message.sender_id == user_id)
        .limit(limit)
        .offset(offset)
        .all()
    )
    return db_chats

@router.get("/c/{chat_id}", response_model=MessageOut)
def get_chat_by_id(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific chat by ID"""
    db_chat = db.query(Message).filter(Message.id == chat_id).first()
    if not db_chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    verify_message_ownership(db_chat, current_user)
    return db_chat

@router.post("/send", response_model=MessageOut)
def send_message(
    msg: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a new message"""
    # Fake LLM response for now
    ai_response = f"AI Response to: {msg.message}"
    
    new_message = Message(
        sender_id=current_user.id,
        message=msg.message,
        response=ai_response,
        collection=msg.collection or shortuuid.uuid()
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

@router.put("/update/{chat_id}", response_model=MessageOut)
def update_chat(
    chat_id: UUID,
    chat: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a chat message"""
    db_chat = db.query(Message).filter(Message.id == chat_id).first()
    if not db_chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    verify_message_ownership(db_chat, current_user)
    
    db_chat.message = chat.message
    if chat.collection:
        db_chat.collection = chat.collection
    
    db.commit()
    db.refresh(db_chat)
    return db_chat

@router.delete("/delete/{chat_id}")
def delete_chat(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a chat message"""
    db_chat = db.query(Message).filter(Message.id == chat_id).first()
    if not db_chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    verify_message_ownership(db_chat, current_user)
    
    db.delete(db_chat)
    db.commit()
    return {"message": "Chat deleted successfully"}