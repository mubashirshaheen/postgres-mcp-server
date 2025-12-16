"""Schemas for AI chat interactions."""
from datetime import datetime

from pydantic import BaseModel


class MCPLogsCreate(BaseModel):
    prompt: str
    response: str
    thread_id: str


class MCPLogsResponse(BaseModel):
    id: int
    prompt: str
    response: str
    thread_id: str
    created_at: datetime

    class Config:
        """ Config """
        from_attributes = True


