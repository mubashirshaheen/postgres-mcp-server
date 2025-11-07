from sqlalchemy.orm import Session
import models
import schemas


def save_chat(db: Session, chat: schemas.AiChatCreate):
    """

    :param db:
    :param chat:
    :return:
    """
    chat_record = models.AIChat(
        prompt=chat.prompt,
        response=chat.response
    )
    db.add(chat_record)
    db.commit()
    db.refresh(chat_record)
    return chat_record
