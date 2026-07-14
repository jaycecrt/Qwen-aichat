"""Parse uploaded files (PDF/DOCX/TXT) into text chunks for the knowledge base."""
from pathlib import Path
from typing import List

# Maximum characters per chunk — keeps it small for precise retrieval
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100  # overlap between adjacent chunks to avoid cutting context


def parse_file(file_path: str) -> List[str]:
    """Parse a file and return a list of text chunks."""
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        text = _parse_pdf(file_path)
    elif ext in (".docx", ".doc"):
        text = _parse_docx(file_path)
    elif ext == ".txt":
        text = _parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return _split_into_chunks(text)


def _parse_txt(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8", errors="ignore")


def _parse_pdf(file_path: str) -> str:
    from PyPDF2 import PdfReader
    reader = PdfReader(file_path)
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n".join(parts)


def _parse_docx(file_path: str) -> str:
    from docx import Document
    doc = Document(file_path)
    parts = []
    for para in doc.paragraphs:
        if para.text.strip():
            parts.append(para.text)
    return "\n".join(parts)


def _split_into_chunks(text: str) -> List[str]:
    """Split long text into overlapping chunks by paragraph, then by length."""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    if not paragraphs:
        return []

    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) < CHUNK_SIZE:
            current = (current + "\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            # When a paragraph alone exceeds chunk size, split it further
            if len(para) > CHUNK_SIZE:
                for i in range(0, len(para), CHUNK_SIZE - CHUNK_OVERLAP):
                    chunks.append(para[i:i + CHUNK_SIZE])
            else:
                current = para
    if current:
        chunks.append(current)
    return chunks
