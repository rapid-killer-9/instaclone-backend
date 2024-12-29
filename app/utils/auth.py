from datetime import datetime, timedelta
import jwt
from typing import Optional
from app.config.settings import SECRET_KEY, ALGORITHM
import hashlib, os

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
    except JWTError:
        return None
