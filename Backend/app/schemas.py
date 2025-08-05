from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    username: str
    email: EmailStr
    password_hash: str

class Message(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    history_id: Optional[str] = None  # PK of the history this message belongs to (optional, will be created if missing)
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None

class History(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str  # PK of the user this history belongs to
    created_at: Optional[datetime] = None


class SummarizeRequest(BaseModel):
    text: str


class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int


class ChatHistory(BaseModel):
    id: Optional[str] = None
    user_id: str
    messages: List[Message]
    created_at: Optional[datetime] = None

