from app.utils.db import get_database
from app.utils.auth import create_access_token, verify_token
from app.models.pydantic import User
import bcrypt

async def authenticate_user(email: str, password: str):
    db = await get_database()
    user = await db.users.find_one({"email": email})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return None
    token = create_access_token({
        "user_id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"]
    })
    return token
