from sqlalchemy.orm import Session
from typing import List, Optional
from models.models import Conversation, Message, KnowledgeChunk
from utils.embedding import cosine_similarity


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


# ── Knowledge Base CRUD ──

def add_knowledge_chunk(db: Session, source_file: str, content: str, embedding_str: str) -> KnowledgeChunk:
    """Add a knowledge chunk with its embedding vector (comma-separated string)."""
    chunk = KnowledgeChunk(source_file=source_file, content=content, embedding=embedding_str)
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return chunk


def search_knowledge(db: Session, query_vec: list[float], top_k: int = 3) -> list[KnowledgeChunk]:
    """Search knowledge chunks by cosine similarity to the query vector. Returns top_k matches."""
    chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.embedding.isnot(None)).all()
    scored = []
    for c in chunks:
        try:
            emb = [float(x) for x in c.embedding.split(",")]
            score = cosine_similarity(query_vec, emb)
            scored.append((score, c))
        except (ValueError, AttributeError):
            continue
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]


def list_knowledge(db: Session) -> list[KnowledgeChunk]:
    """List all knowledge chunks, newest first."""
    return db.query(KnowledgeChunk).order_by(KnowledgeChunk.created_at.desc()).all()


def delete_knowledge(db: Session, chunk_id: int) -> bool:
    """Delete a single knowledge chunk. Returns True if deleted."""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        return False
    db.delete(chunk)
    db.commit()
    return True
