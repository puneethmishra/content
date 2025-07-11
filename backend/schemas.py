from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

# Message schemas
class MessageBase(BaseModel):
    phone_number: str
    contact_name: str = ""
    message_text: str
    message_type: str = "text"

class MessageCreate(MessageBase):
    is_incoming: bool = True
    raw_data: Optional[str] = None

class MessageResponse(MessageBase):
    id: int
    timestamp: datetime
    is_incoming: bool
    parent_message_id: Optional[int] = None
    classification: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True

# Classification schemas
class ClassificationBase(BaseModel):
    category: str
    confidence: float = 0.0
    tags: str = ""
    sentiment: str = "neutral"

class ClassificationCreate(ClassificationBase):
    message_id: int

class ClassificationResponse(ClassificationBase):
    id: int
    message_id: int
    created_at: datetime
    count: Optional[int] = None
    avg_confidence: Optional[float] = None
    sentiments: Optional[Dict[str, int]] = None
    
    class Config:
        orm_mode = True

# Auto Response schemas
class AutoResponseBase(BaseModel):
    name: str
    category: str
    template: str
    is_active: bool = True
    priority: int = 1
    conditions: Optional[str] = None

class AutoResponseCreate(AutoResponseBase):
    pass

class AutoResponseResponse(AutoResponseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Contact schemas
class ContactBase(BaseModel):
    phone_number: str
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_picture: Optional[str] = None
    status: Optional[str] = None
    is_business: bool = False
    tags: Optional[str] = None
    notes: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: Optional[int] = None
    total_messages: Optional[int] = None
    incoming_count: Optional[int] = None
    outgoing_count: Optional[int] = None
    last_message_time: Optional[datetime] = None
    last_message_text: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# Settings schemas
class SettingsBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class SettingsCreate(SettingsBase):
    pass

class SettingsResponse(SettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Campaign schemas
class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    message_template: str
    target_contacts: str  # JSON array
    scheduled_at: Optional[datetime] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignResponse(CampaignBase):
    id: int
    status: str
    sent_count: int = 0
    failed_count: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

# Custom request/response schemas
class BroadcastMessageRequest(BaseModel):
    phone_numbers: List[str]
    message_text: str
    campaign_id: Optional[str] = None

class MessageStats(BaseModel):
    total_messages: int
    total_incoming: int
    total_outgoing: int
    total_contacts: int
    recent_messages: int
    category_stats: Dict[str, int]

class WhatsAppStatus(BaseModel):
    connected: bool
    phone_number: Optional[str] = None
    status: str
    last_seen: Optional[datetime] = None

class SendMessageRequest(BaseModel):
    phone_number: str
    message_text: str
    message_type: str = "text"

class ClassifyMessageRequest(BaseModel):
    message_text: str

class ClassifyMessageResponse(BaseModel):
    category: str
    confidence: float
    tags: List[str]
    sentiment: str
    reasoning: Optional[str] = None