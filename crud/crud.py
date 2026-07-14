from sqlalchemy.orm import Session
from typing import List, Optional
from models.models import Conversation, Message


def create_conversation(db: Session, title: str = "New Chat") -> Conversation:
    conv = Conversation(title=title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def get_conversation(db: Session, conv_id: int) -> Optional[Conversation]:
    return db.query(Conversation).filter(Conversation.id == conv_id).first()


def list_conversations(db: Session) -> List[Conversation]:
    return db.query(Conversation).order_by(Conversation.created_at.desc()).all()


def add_message(db: Session, conv_id: int, role: str, content: str) -> Message:
    msg = Message(conversation_id=conv_id, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_messages(db: Session, conv_id: int) -> List[Message]:
    return (
        db.query(Message)
        .filter(Message.conversation_id == conv_id)
        .order_by(Message.created_at.asc())
        .all()
    )


def update_conversation_title(db: Session, conv_id: int, title: str):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if conv:
        conv.title = title
        db.commit()


def delete_conversation(db: Session, conv_id: int) -> bool:
    """Delete a conversation and all its messages. Returns True if deleted, False if not found."""
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        return False
    # Delete all messages first, then the conversation
    db.query(Message).filter(Message.conversation_id == conv_id).delete()
    db.delete(conv)
    db.commit()
    return True
