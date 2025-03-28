from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Message
from schemas import MessageCreate, MessageOut

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/send", response_model=MessageOut)
def send_message(msg: MessageCreate, db: Session = Depends(get_db)):
    # Fake LLM response for now
    ai_response = f"AI Response to: {msg.message}"
    
    new_message = Message(sender_id=1, message=msg.message, response=ai_response)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return new_message
