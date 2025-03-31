from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID  # Use UUID in PostgreSQL (or `sqlalchemy.types.UUID` for other DBs)
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid  # For UUID generation
import shortuuid  # For short, readable IDs

class User(Base):
    __tablename__ = "users"
    
    # Using UUID as primary key
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,  # Auto-generate UUID on creation
        unique=True, 
        index=True
    )
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default='user')
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"

    # Using UUID as primary key
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,  # Auto-generate UUID on creation
        unique=True, 
        index=True
    )
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # Match UUID type
    message = Column(Text, nullable=False)
    response = Column(Text)
    collection = Column(String, index=True, nullable=False, default=shortuuid.uuid)  # ShortUUID for collection
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User")