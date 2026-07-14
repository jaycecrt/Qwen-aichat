"""Simple token-based auth for protecting write operations."""
import secrets
import time
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "root")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# In-memory token store: token -> expiry timestamp
_tokens: dict[str, float] = {}


def verify_credentials(username: str, password: str) -> str | None:
    """Return a new token if username/password match, else None."""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        token = secrets.token_hex(32)
        _tokens[token] = time.time() + 3600 * 24  # 24-hour expiry
        return token
    return None


def verify_token(token: str) -> bool:
    """Check whether a bearer token is valid and not expired."""
    if token in _tokens:
        if _tokens[token] > time.time():
            return True
        del _tokens[token]  # expired — clean up
    return False
