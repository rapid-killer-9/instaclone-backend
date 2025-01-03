from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError
from typing import Optional
from app.config.settings import SECRET_KEY, ALGORITHM
import hashlib, os
from fastapi import Depends, HTTPException, Request
from app.models.db import serialize_document
from app.services.user_service import get_user_by_email


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    salt = hashlib.sha256(os.urandom(60)).hexdigest()
    to_encode.update({"salt": salt, "exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except PyJWTError:
        return None

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        scheme, token = auth_header.split(" ", 1)
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload.")
    
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    
    return serialize_document(user)
