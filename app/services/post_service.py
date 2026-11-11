from datetime import datetime
from typing import Optional
from bson import ObjectId
from app.utils.db import get_database
from app.models.db import PostDB, serialize_document


async def create_post(post_data: dict) -> dict:
    db = get_database()

    post_db = PostDB(
        caption=post_data["caption"],
        media_url=post_data["media_url"],
        category=post_data["category"],
        posted_at=post_data["posted_at"],
        publisher_id=post_data["publisher_id"],
        description=post_data["description"],
        music_url=post_data.get("music_url"),
        likes=post_data.get("likes", []),
        comments=post_data.get("comments", []),
        hashtags=post_data.get("hashtags", []),
        tagged_users=post_data.get("tagged_users", []),
    )

    result = await db.posts.insert_one(post_db.to_dict())
    post_id = str(result.inserted_id)

    await db.users.update_one(
        {"_id": ObjectId(post_data["publisher_id"])},
        {"$addToSet": {"posts": post_id}},
    )
    for user_id in post_db.tagged_users:
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"tagged_posts": post_id}},
        )

    post_db._id = post_id
    return serialize_document(post_db.to_dict())


async def get_post(post_id: str) -> Optional[dict]:
    db = get_database()
    if not ObjectId.is_valid(post_id):
        raise ValueError("Invalid post ID.")
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    return serialize_document(post)


async def get_posts(skip: int, limit: int, category: Optional[str] = None) -> list:
    db = get_database()
    query = {"category": category} if category else {}
    cursor = db.posts.find(query).sort("posted_at", -1).skip(skip).limit(limit)
    return serialize_document(await cursor.to_list(length=limit))


async def get_feed(user_id: str, skip: int, limit: int) -> list:
    db = get_database()
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID.")
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise ValueError("User not found.")

    following_ids = [str(oid) for oid in user.get("following", [])]
    cursor = db.posts.find({"publisher_id": {"$in": following_ids}}).sort("posted_at", -1).skip(skip).limit(limit)
    return serialize_document(await cursor.to_list(length=limit))


async def delete_post(post_id: str, user_id: str) -> bool:
    db = get_database()
    if not ObjectId.is_valid(post_id):
        raise ValueError("Invalid post ID.")
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        return False
    if str(post["publisher_id"]) != user_id:
        raise PermissionError("Not authorised to delete this post.")

    await db.posts.delete_one({"_id": ObjectId(post_id)})
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"posts": post_id}},
    )
    for tagged_id in post.get("tagged_users", []):
        await db.users.update_one(
            {"_id": ObjectId(tagged_id)},
            {"$pull": {"tagged_posts": post_id}},
        )
    return True


async def like_post(post_id: str, user_id: str) -> None:
    db = get_database()
    if not ObjectId.is_valid(post_id):
        raise ValueError("Invalid post ID.")
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise ValueError("Post not found.")
    if user_id in post.get("likes", []):
        raise ValueError("Post already liked.")
    await db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$addToSet": {"likes": user_id}},
    )


async def unlike_post(post_id: str, user_id: str) -> None:
    db = get_database()
    if not ObjectId.is_valid(post_id):
        raise ValueError("Invalid post ID.")
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise ValueError("Post not found.")
    if user_id not in post.get("likes", []):
        raise ValueError("Post not liked.")
    await db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$pull": {"likes": user_id}},
    )


async def add_comment(post_id: str, user_id: str, text: str) -> dict:
    db = get_database()
    if not ObjectId.is_valid(post_id):
        raise ValueError("Invalid post ID.")
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise ValueError("Post not found.")

    comment = {
        "_id": ObjectId(),
        "user_id": user_id,
        "text": text,
        "created_at": datetime.utcnow(),
    }
    await db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": comment}},
    )
    return serialize_document(comment)
