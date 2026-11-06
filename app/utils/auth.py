from datetime import datetime, timedelta
from typing import Optional
import hashlib
import os
import jwt
from jwt import PyJWTError
from fastapi import HTTPException, Request
from app.config.settings import SECRET_KEY, ALGORITHM
from app.models.db import serialize_document


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    salt = hashlib.sha256(os.urandom(60)).hexdigest()
    to_encode.update({"salt": salt, "exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except PyJWTError:
        return None


async def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing.")

    parts = auth_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format.")

    payload = verify_token(parts[1])
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload.")

    # Imported here to avoid a circular import at module load time.
    from app.services.user_service import get_user_by_email
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")

    return serialize_document(user)
