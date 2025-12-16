from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database import Base


class MCPLogs(Base):
    __tablename__ = "mcp_logs"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String)
    response = Column(Text)
    thread_id = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())