from datetime import datetime
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
