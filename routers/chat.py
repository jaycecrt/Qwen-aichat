import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from config.db_conf import get_db
from schemas.schemas import ChatRequest
from crud.crud import (
    create_conversation,
    get_conversation,
    list_conversations,
    add_message,
    get_messages,
    update_conversation_title,
    delete_conversation,
)
from utils.qwen_client import stream_chat

router = APIRouter(prefix="/api", tags=["chat"])


def _build_messages_for_api(db: Session, conv_id: int) -> list[dict]:
    """Convert DB message rows to the format Qwen API expects."""
    msgs = get_messages(db, conv_id)
    return [{"role": m.role, "content": m.content} for m in msgs]


@router.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """
    Core chat endpoint with SSE streaming.
    Uses def (sync) because the OpenAI SDK streaming call is synchronous.
    FastAPI runs sync routes in a threadpool automatically.
    """
    # 1. Get or create conversation
    conv_id = req.conversation_id
    if conv_id:
        conv = get_conversation(db, conv_id)
        if not conv:
            conv = create_conversation(db)
            conv_id = conv.id
    else:
        conv = create_conversation(db)
        conv_id = conv.id

    # 2. Save user message
    add_message(db, conv_id, "user", req.message)

    # 3. Build full message history for the AI call
    api_messages = _build_messages_for_api(db, conv_id)

    # 4. Auto-title: use first message as conversation title
    if conv.title == "New Chat":
        title = req.message[:50] + ("..." if len(req.message) > 50 else "")
        update_conversation_title(db, conv_id, title)

    # 5. SSE streaming generator
    def generate():
        full_response = ""
        try:
            for token in stream_chat(api_messages):
                full_response += token
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        # Save assistant message after stream completes
        if full_response:
            add_message(db, conv_id, "assistant", full_response)
        yield f"data: {json.dumps({'done': True, 'conversation_id': conv_id})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/conversations")
def list_convs(db: Session = Depends(get_db)):
    """Return list of all conversations (sidebar)."""
    convs = list_conversations(db)
    return [
        {"id": c.id, "title": c.title, "created_at": c.created_at.isoformat()}
        for c in convs
    ]


@router.get("/conversations/{conv_id}")
def get_conv(conv_id: int, db: Session = Depends(get_db)):
    """Return a single conversation with all its messages."""
    conv = get_conversation(db, conv_id)
    if not conv:
        return {"error": "Conversation not found"}
    return {
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at.isoformat(),
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
            }
            for m in conv.messages
        ],
    }


@router.delete("/conversations/{conv_id}")
def delete_conv(conv_id: int, db: Session = Depends(get_db)):
    """Delete a conversation and all its messages."""
    ok = delete_conversation(db, conv_id)
    if not ok:
        return {"error": "Conversation not found"}
    return {"ok": True}
