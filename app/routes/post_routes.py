from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Request
from app.models.pydantic import PostCreateRequest
from app.utils.post_validator import (
    validate_category,
    validate_caption,
    validate_description,
    validate_hashtags,
    validate_media_url,
    validate_music_url,
)
from app.utils.auth import get_current_user
from app.utils.rate_limit import limiter
from app.services.post_service import create_post
from app.services.user_service import get_user_by_username

router = APIRouter()


@router.post("/", status_code=201)
@limiter.limit("30/minute")
async def create_new_post(
    request: Request,
    post: PostCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["_id"]
    if not validate_category(post.category):
        raise HTTPException(status_code=400, detail="Invalid category.")
    if not validate_caption(post.caption):
        raise HTTPException(status_code=400, detail="Caption must be non-empty and at most 100 characters.")
    if post.description and not validate_description(post.description):
        raise HTTPException(status_code=400, detail="Description must be at most 500 characters.")
    if post.hashtags and not validate_hashtags(post.hashtags):
        raise HTTPException(status_code=400, detail="Provide at most 10 hashtags, each at most 20 characters.")
    if not validate_media_url(post.media_url):
        raise HTTPException(status_code=400, detail="Media URL must start with http:// or https://.")
    if post.music_url and not validate_music_url(post.music_url):
        raise HTTPException(status_code=400, detail="Music URL must start with http:// or https://.")

    valid_tagged_ids = []
    for username in (post.tagged_users or []):
        user = await get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=400, detail=f"Tagged user '{username}' not found.")
        valid_tagged_ids.append(user["_id"])

    post_data = post.model_dump()
    post_data.update({
        "publisher_id": user_id,
        "posted_at": datetime.utcnow(),
        "likes": [],
        "comments": [],
        "tagged_users": valid_tagged_ids,
    })

    try:
        new_post = await create_post(post_data)
        return {"message": "Post created successfully.", "post": new_post}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
