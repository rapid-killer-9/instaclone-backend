from app.utils.db import get_database
from app.models.db import serialize_document
from bson import ObjectId

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
        {"_id": ObjectId(user_id)},  
        {"$set": update_data},
        return_document=True
    )
    return serialize_document(updated_user)

async def follow_user(user_id: str, follow_user_id: str):
    db = await get_database()
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(follow_user_id):
        raise ValueError("Invalid user ID format.")
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if ObjectId(follow_user_id) in user["following"]:
        raise ValueError("User is already following the target user.")
    if user_id == follow_user_id:
        raise ValueError("User cannot follow itself.")
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"following": ObjectId(follow_user_id)}}
    )
    await db.users.update_one(
        {"_id": ObjectId(follow_user_id)},
        {"$addToSet": {"followers": ObjectId(user_id)}}
    )

async def unfollow_user(user_id: str, unfollow_user_id: str):
    db = await get_database()
    if not ObjectId.is_valid(user_id) or not ObjectId.is_valid(unfollow_user_id):
        raise ValueError("Invalid user ID format.")
    if user_id == unfollow_user_id:
        raise ValueError("User cannot unfollow itself.")
    if ObjectId(unfollow_user_id) not in (await db.users.find_one({"_id": ObjectId(user_id)})["following"]):
        raise ValueError("User is not following the target user.")
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"following": ObjectId(unfollow_user_id)}}
    )
    await db.users.update_one(
        {"_id": ObjectId(unfollow_user_id)},
        {"$pull": {"followers": ObjectId(user_id)}}
    )

async def get_followers(user_id: str):
    db = await get_database()
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID format.")
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    followers = await db.users.find({"_id": {"$in": user["followers"]}}).to_list(length=None)
    updated_followers = []
    for follower in followers:
        updated_followers.append({
            "username": follower["username"],
            "full_name": follower["full_name"],
            "_id": str(follower["_id"])
        })
    return updated_followers

async def get_following(user_id: str):
    db = await get_database()
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID format.")
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    following = await db.users.find({"_id": {"$in": user["following"]}}).to_list(length=None)
    updated_following = []
    for follow_user in following:
        updated_following.append({
            "username": follow_user["username"],
            "full_name": follow_user["full_name"],
            "_id": str(follow_user["_id"])
        })
    return updated_following

