"""Knowledge base management API — upload / list / delete."""
import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from config.db_conf import get_db
from crud.crud import add_knowledge_chunk, list_knowledge, delete_knowledge
from utils.knowledge_parser import parse_file
from utils.embedding import generate_embedding
from utils.auth import verify_token

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


def require_auth(authorization: str = Header(None)) -> None:
    """Raise 401 if the Authorization header is missing or invalid."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="请先登录")
    token = authorization[7:]
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")


@router.post("/upload")
def upload_knowledge(file: UploadFile = File(...), db: Session = Depends(get_db), _=Depends(require_auth)):
    """Upload a PDF/DOCX/TXT file, parse it into chunks, embed and store each chunk."""
    # Save uploaded file to a temp location
    suffix = os.path.splitext(file.filename or "upload.txt")[1] or ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        chunks = parse_file(tmp_path)
    finally:
        os.unlink(tmp_path)  # clean up temp file

    if not chunks:
        return {"ok": True, "chunks_added": 0}

    for content in chunks:
        vec = generate_embedding(content)
        vec_str = ",".join(f"{v:.8f}" for v in vec)
        add_knowledge_chunk(db, source_file=file.filename or "unknown", content=content, embedding_str=vec_str)

    return {"ok": True, "chunks_added": len(chunks)}


@router.get("")
def list_all_knowledge(db: Session = Depends(get_db)):
    """List all knowledge chunks."""
    chunks = list_knowledge(db)
    return [
        {"id": c.id, "source_file": c.source_file, "content": c.content, "created_at": c.created_at.isoformat()}
        for c in chunks
    ]


@router.delete("/{chunk_id}")
def delete_knowledge_chunk(chunk_id: int, db: Session = Depends(get_db), _=Depends(require_auth)):
    """Delete a knowledge chunk."""
    ok = delete_knowledge(db, chunk_id)
    return {"ok": ok}
