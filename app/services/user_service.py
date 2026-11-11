import bcrypt
from bson import ObjectId
from pymongo import ReturnDocument
from app.utils.db import get_database
from app.models.db import serialize_document


async def get_user_by_id(user_id: str) -> dict | None:
    db = get_database()
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID format.")
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    return serialize_document(user)


async def get_user_by_email(email: str) -> dict | None:
    db = get_database()
    user = await db.users.find_one({"email": email})
    return serialize_document(user)


async def get_user_by_username(username: str) -> dict | None:
    db = get_database()
    user = await db.users.find_one({"username": username})
    return serialize_document(user)


_ALLOWED_UPDATE_FIELDS = {"full_name", "username", "email", "password"}


async def update_user(user_id: str, update_data: dict) -> dict | None:
    db = get_database()
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID format.")

    update_data = {k: v for k, v in update_data.items() if k in _ALLOWED_UPDATE_FIELDS}
    if not update_data:
        raise ValueError("No valid fields to update.")

    if "email" in update_data:
        existing = await db.users.find_one({"email": update_data["email"], "_id": {"$ne": ObjectId(user_id)}})
        if existing:
            raise ValueError("Email already in use.")

    if "username" in update_data:
        existing = await db.users.find_one({"username": update_data["username"], "_id": {"$ne": ObjectId(user_id)}})
        if existing:
            raise ValueError("Username already in use.")

    if "password" in update_data:
        update_data["password"] = bcrypt.hashpw(
            update_data["password"].encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    updated_user = await db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )
    return serialize_document(updated_user)


async def follow_user(user_id: str, follow_user_id: str) -> None:
    db = get_database()
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(follow_user_id):
        raise ValueError("Invalid user ID format.")
    if user_id == follow_user_id:
        raise ValueError("A user cannot follow themselves.")

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise ValueError("User not found.")
    if ObjectId(follow_user_id) in user.get("following", []):
        raise ValueError("Already following this user.")

    target = await db.users.find_one({"_id": ObjectId(follow_user_id)})
    if not target:
        raise ValueError("Target user not found.")

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"following": ObjectId(follow_user_id)}},
    )
    await db.users.update_one(
        {"_id": ObjectId(follow_user_id)},
        {"$addToSet": {"followers": ObjectId(user_id)}},
    )


async def unfollow_user(user_id: str, unfollow_user_id: str) -> None:
    db = get_database()
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(unfollow_user_id):
        raise ValueError("Invalid user ID format.")
    if user_id == unfollow_user_id:
        raise ValueError("A user cannot unfollow themselves.")

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise ValueError("User not found.")
    if ObjectId(unfollow_user_id) not in user.get("following", []):
        raise ValueError("Not following this user.")

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"following": ObjectId(unfollow_user_id)}},
    )
    await db.users.update_one(
        {"_id": ObjectId(unfollow_user_id)},
        {"$pull": {"followers": ObjectId(user_id)}},
    )


async def get_followers(user_id: str, skip: int, limit: int) -> tuple[list, int]:
    db = get_database()
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID format.")
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"followers": 1})
    if not user:
        raise ValueError("User not found.")
    follower_ids = user.get("followers", [])
    total = len(follower_ids)
    docs = await db.users.find(
        {"_id": {"$in": follower_ids}},
        {"username": 1, "full_name": 1},
    ).skip(skip).limit(limit).to_list(length=limit)
    return [{"_id": str(d["_id"]), "username": d["username"], "full_name": d["full_name"]} for d in docs], total


async def get_following(user_id: str, skip: int, limit: int) -> tuple[list, int]:
    db = get_database()
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID format.")
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"following": 1})
    if not user:
        raise ValueError("User not found.")
    following_ids = user.get("following", [])
    total = len(following_ids)
    docs = await db.users.find(
        {"_id": {"$in": following_ids}},
        {"username": 1, "full_name": 1},
    ).skip(skip).limit(limit).to_list(length=limit)
    return [{"_id": str(d["_id"]), "username": d["username"], "full_name": d["full_name"]} for d in docs], total
