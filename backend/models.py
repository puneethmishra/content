from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), index=True, nullable=False)
    contact_name = Column(String(100), default="")
    message_text = Column(Text)
    message_type = Column(String(20), default="text")  # text, image, video, audio, document
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_incoming = Column(Boolean, default=True)
    parent_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    raw_data = Column(Text)  # JSON string of raw WhatsApp data
    
    # Relationships
    parent_message = relationship("Message", remote_side=[id])
    classification = relationship("Classification", back_populates="message", uselist=False)

class Classification(Base):
    __tablename__ = "classifications"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), unique=True)
    category = Column(String(50), index=True)  # support, sales, general, complaint, etc.
    confidence = Column(Float, default=0.0)
    tags = Column(String(200))  # Comma-separated tags
    sentiment = Column(String(20), default="neutral")  # positive, negative, neutral
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    message = relationship("Message", back_populates="classification")

class AutoResponse(Base):
    __tablename__ = "auto_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), index=True)  # Category to trigger this response
    template = Column(Text, nullable=False)  # Response template with placeholders
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # Higher number = higher priority
    conditions = Column(Text)  # JSON string of additional conditions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True)
    name = Column(String(100))
    first_name = Column(String(50))
    last_name = Column(String(50))
    profile_picture = Column(String(500))  # URL to profile picture
    status = Column(String(200))  # WhatsApp status
    is_business = Column(Boolean, default=False)
    tags = Column(String(200))  # Comma-separated tags
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True)
    value = Column(Text)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    message_template = Column(Text, nullable=False)
    target_contacts = Column(Text)  # JSON array of phone numbers
    status = Column(String(20), default="draft")  # draft, active, completed, failed
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True)
    metric_name = Column(String(50), index=True)
    metric_value = Column(Float)
    extra_data = Column("metadata", Text)  # JSON string for additional data ('metadata' attr name is reserved by SQLAlchemy)