from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from app.models.pydantic import PostCreateRequest, CommentCreateRequest, PostCategory
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
from app.utils.pagination import PaginationParams
from app.services.post_service import (
    create_post,
    get_post,
    get_posts,
    get_feed,
    delete_post,
    like_post,
    unlike_post,
    add_comment,
)
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


@router.get("/feed")
async def get_feed_route(
    current_user: dict = Depends(get_current_user),
    pagination: PaginationParams = Depends(),
):
    try:
        posts = await get_feed(current_user["_id"], pagination.skip, pagination.limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"posts": posts, "page": pagination.page, "limit": pagination.limit}


@router.get("/")
async def list_posts(
    category: Optional[PostCategory] = None,
    pagination: PaginationParams = Depends(),
):
    posts = await get_posts(pagination.skip, pagination.limit, category.value if category else None)
    return {"posts": posts, "page": pagination.page, "limit": pagination.limit}


@router.get("/{post_id}")
async def get_post_route(post_id: str):
    try:
        post = await get_post(post_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    return {"post": post}


@router.delete("/{post_id}", status_code=204)
async def delete_post_route(post_id: str, current_user: dict = Depends(get_current_user)):
    try:
        found = await delete_post(post_id, current_user["_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    if not found:
        raise HTTPException(status_code=404, detail="Post not found.")


@router.post("/{post_id}/like", status_code=200)
@limiter.limit("60/minute")
async def like_post_route(
    request: Request,
    post_id: str,
    current_user: dict = Depends(get_current_user),
):
    try:
        await like_post(post_id, current_user["_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Post liked."}


@router.delete("/{post_id}/like", status_code=200)
async def unlike_post_route(post_id: str, current_user: dict = Depends(get_current_user)):
    try:
        await unlike_post(post_id, current_user["_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Like removed."}


@router.post("/{post_id}/comments", status_code=201)
@limiter.limit("30/minute")
async def add_comment_route(
    request: Request,
    post_id: str,
    data: CommentCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        comment = await add_comment(post_id, current_user["_id"], data.text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Comment added.", "comment": comment}
