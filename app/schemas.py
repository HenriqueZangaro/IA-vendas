from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ThreadBase(BaseModel):
    whatsapp_number: str = Field(..., min_length=1, max_length=20)
    external_thread_id: Optional[str] = None

class ThreadCreate(ThreadBase):
    pass

class ThreadResponse(ThreadBase):
    thread_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    thread_id: int
    status: str = "iniciado"
    messages: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(ConversationBase):
    id: int

    class Config:
        from_attributes = True
