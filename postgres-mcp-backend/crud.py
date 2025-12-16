"""CRUD operations for MCPLogs."""
from sqlalchemy.orm import Session
import models
import schemas


def save_chat(db: Session, chat: schemas.MCPLogsCreate):
    """

    :param db:
    :param chat:
    :type db: Session
    :type chat: schemas.MCPLogsCreate
    :return:
    """
    chat_record = models.MCPLogs(
        prompt=chat.prompt,
        response=chat.response,
        thread_id=chat.thread_id
    )
    db.add(chat_record)
    db.commit()
    db.refresh(chat_record)
    return chat_record
