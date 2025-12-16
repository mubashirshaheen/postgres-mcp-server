"""Example of using PostgresMCPServer agent."""
import logging
import uuid
from typing import Optional

from asgiref.sync import async_to_sync
from fastapi import APIRouter, Depends
from pydantic import BaseModel

import crud
import models
import schemas
import config
from database import SessionLocal, engine
from postgresmcpserver import PostgresMCPServer
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    question: str
    thread_id: Optional[str] = None


def get_db():
    """
        Get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    :param
    request:
    db:
    :return:
    """
    prompt = request.question
    thread_id = request.thread_id
    if not thread_id:
        thread_id = str(uuid.uuid4())
    agent = PostgresMCPServer(region=config.region)

    answer = async_to_sync(agent.run_agent)(prompt, thread_id)
    # Save to DB
    chat_data = schemas.MCPLogsCreate(prompt=prompt, response=str(answer), thread_id=thread_id)
    crud.save_chat(db, chat_data)

    return {"thread_id": thread_id, "answer": answer}
