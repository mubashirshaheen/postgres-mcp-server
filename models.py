from sqlalchemy import Column, Integer, String, Text
from database import Base


class AIChat(Base):
    __tablename__ = "aichat"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, index=True)
    response = Column(Text)
    thread_id = Column(String, index=True)

