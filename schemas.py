"""Schemas for AI chat interactions."""
from pydantic import BaseModel


class AiChatCreate(BaseModel):
    prompt: str
    response: str
    thread_id: str


class AiChatResponse(BaseModel):
    id: int
    prompt: str
    response: str
    thread_id: str

    class Config:
        from_attributes = True


