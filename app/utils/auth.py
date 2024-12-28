from datetime import datetime, timedelta
import jwt
from app.config.settings import JWT_SECRET_KEY

def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None
