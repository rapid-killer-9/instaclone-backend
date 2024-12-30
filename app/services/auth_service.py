from app.utils.db import get_database
from app.utils.auth import create_access_token
import bcrypt
from typing import Optional

async def create_user(email: str, password: str, full_name: Optional[str], username: str):
    db = await get_database()
    
    if await db.users.find_one({"email": email}):
        raise ValueError("Email already in use.")
    if await db.users.find_one({"username": username}):
        raise ValueError("Username already in use.")

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    

    user_data = {
        "email": email,
        "password": hashed_password,
        "full_name": full_name,
        "username": username,
        "posts": [],
        "followers": [],
        "following": []
    }
    
    result = await db.users.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)

    token_payload = {
        "user_id": user_data["_id"],
        "username": user_data["username"],
        "email": user_data["email"]
    }

    token = create_access_token(token_payload)

    user_data.update({"access_token": token})
    return user_data


async def authenticate_user(email: str, password: str):
    db = await get_database()
    user = await db.users.find_one({"email": email})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        return None
    token = create_access_token({
        "user_id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"]
    })
    return token
