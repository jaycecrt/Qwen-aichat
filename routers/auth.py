"""Auth router — login endpoint."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.auth import verify_credentials

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(body: LoginRequest):
    token = verify_credentials(body.username, body.password)
    if token is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return {"ok": True, "token": token}
