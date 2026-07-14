from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from config.db_conf import engine, Base
from routers.chat import router as chat_router
from pathlib import Path

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Q&A Chat", version="1.0.0")

# Include chat API routes (/api/chat, /api/conversations, etc.)
app.include_router(chat_router)

# Read the static HTML frontend once at startup
INDEX_HTML = (Path(__file__).parent / "view" / "templates" / "index.html").read_text(encoding="utf-8")


@app.get("/")
def index():
    """Serve the chat interface."""
    return HTMLResponse(content=INDEX_HTML)
