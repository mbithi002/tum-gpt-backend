from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Message, User
from schemas import MessageCreate, MessageOut

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/", response_model=list[MessageOut])
def get_all_chats(*, limit: int = 25, offset: int = 25, db: Session = Depends(get_db)):
    # TODO check current_user session and verify admin role
    db_chats = db.query(Message).limit(limit).offset(offset)
    if db_chats is None:
        raise HTTPException(
            ststus_code=404,
            detail="No chats found"
        )
    return db_chats

@router.get("/user/{user_id}", response_model=list[MessageOut])
def get_my_chats(*, limit: int = 25, offset: int = 25 ,user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    db_chats = db.query(Message).limit(limit).offset(offset).filter(Message.sender_id == user_id)
    if db_chats is None:
        raise HTTPException(
            status_code=404,
            detail="chats not found"
        )
    return db_chats

@router.get("/c/{chat_id}", response_model=MessageOut)
def get_chat_by_id(chat_id: int, db: Session = Depends(get_db)):
    db_chat = db.query(Message).filter(Message.id == chat_id).first()
    if db_chat is None:
        raise HTTPException(
            status_code=404,
            detail="chat not found"
        )
    return db_chat

@router.post("/send")
def send_message(msg: MessageCreate, db: Session = Depends(get_db)):
    # Fake LLM response for now
    ai_response = f"AI Response to: {msg.message}"
    
    new_message = Message(sender_id=1, message=msg.message, response=ai_response)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return new_message

@router.put("/update/{chat_id}", response_model=MessageOut)
def update_chat(chat: MessageCreate, chat_id: int, db: Session = Depends(get_db)):
    db_chat = db.query(Message).filter(Message.id == chat_id).first()
    if db_chat is None:
        raise HTTPException(
            status_code=404,
            detail='Chat not found'
        )
    db_chat.message = MessageCreate.message
    db.commit()
    db.refresh(db_chat)
    return db_chat

@router.delete("/delete/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    db_chat = db.query(Message).filter(Message.id == chat_id).first()
    if db_chat is None:
        raise HTTPException(
            status_code=404,
            detail="Chat not found"
        )
    db.delete(db_chat)
    db.commit()
    return {
        "message": "Chat deleted"
    }
