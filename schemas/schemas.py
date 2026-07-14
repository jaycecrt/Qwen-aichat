from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[int] = Field(None)


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationListItem(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True


class KnowledgeUploadResponse(BaseModel):
    ok: bool
    chunks_added: int


class KnowledgeItem(BaseModel):
    id: int
    source_file: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
