from app.utils.db import get_database, serialize_document
from typing import Optional
from bson import ObjectId
import bcrypt

async def create_user(email: str, password: str, full_name: Optional[str], username: str):
    db = await get_database()
    
    # Check if email or username already exists
    if await db.users.find_one({"email": email}):
        raise ValueError("Email already in use.")
    if await db.users.find_one({"username": username}):
        raise ValueError("Username already in use.")

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    user_data = {
        "email": email,
        "password": hashed_password.decode('utf-8'),
        "full_name": full_name,
        "username": username,
    }
    
    result = await db.users.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)
    return user_data

async def get_user_by_email(email: str):
    db = await get_database()
    user = await db.users.find_one({"email": email})
    return serialize_document(user)

async def get_user_by_username(username: str):
    db = await get_database()
    user = await db.users.find_one({"username": username})
    return serialize_document(user)

async def update_user(user_id: str, update_data: dict):
    db = await get_database()
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID format.")
    
    updated_user = await db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},  # Convert string ID to ObjectId
        {"$set": update_data},
        return_document=True
    )
    return serialize_document(updated_user)
