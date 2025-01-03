from app.models.db import *
from app.utils.db import get_database

async def create_post(post: PostDB):
    db = await get_database()

    post_db = PostDB(
        caption=post['caption'],
        media_url=post['media_url'],
        category=post['category'],
        posted_at=post['posted_at'],
        publisher_id=post['publisher_id'],
        description=post['description'],
        music_url=post['music_url'],
        likes=post['likes'],
        comments=post['comments'],
        hashtags=post['hashtags'],
        tagged_users=post['tagged_users']
    )

    result = await db.posts.insert_one(post_db.to_dict())
    post_db._id = str(result.inserted_id)


    await db.users.update_one(
        {"_id": ObjectId(post['publisher_id'])},
        {"$addToSet": {"posts": post_db._id}}
    )

    for user_id in post_db.tagged_users:
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"tagged_posts": post_db._id}}
        )

    return serialize_document(post_db.to_dict())