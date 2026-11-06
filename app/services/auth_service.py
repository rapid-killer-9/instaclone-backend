from typing import Optional
import bcrypt
from app.utils.db import get_database
from app.utils.auth import create_access_token
from app.models.db import UserDB


async def create_user(email: str, password: str, full_name: str, username: str) -> dict:
    db = get_database()

    if await db.users.find_one({"email": email}):
        raise ValueError("Email already in use.")
    if await db.users.find_one({"username": username}):
        raise ValueError("Username already in use.")

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    user_db = UserDB(
        email=email,
        password=hashed_password,
        full_name=full_name,
        username=username,
    )

    result = await db.users.insert_one(user_db.__dict__)
    user_id = str(result.inserted_id)

    token = create_access_token({
        "user_id": user_id,
        "username": user_db.username,
        "email": user_db.email,
    })

    return {
        "email": user_db.email,
        "full_name": user_db.full_name,
        "username": user_db.username,
        "access_token": token,
    }


async def authenticate_user(email: str, password: str) -> Optional[str]:
    db = get_database()
    user = await db.users.find_one({"email": email})
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return None
    return create_access_token({
        "user_id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
    })
