from fastapi import APIRouter, HTTPException, Body, Depends
from app.models.pydantic import PostCreateRequest
from app.utils.post_validator import *
from app.utils.auth import get_current_user
from app.services.post_service import *
from app.services.user_service import get_user_by_username

router = APIRouter()

@router.post("/")
async def create_new_post(post: PostCreateRequest, user_id: str = Depends(get_current_user)):
    user_id = user_id["_id"]
    try:
        if not validate_category(post.category):
            raise HTTPException(status_code=400, detail="Invalid category")
        if not validate_caption(post.caption):
            raise HTTPException(status_code=400, detail="Invalid caption")
        if post.description and not validate_description(post.description):
            raise HTTPException(status_code=400, detail="Invalid description")
        if post.hashtags and not validate_hashtags(post.hashtags):
            raise HTTPException(status_code=400, detail="Invalid hashtags")
        if post.media_url and not validate_media_url(post.media_url):
            raise HTTPException(status_code=400, detail="Invalid media url")
        if post.music_url and not validate_music_url(post.music_url):
            raise HTTPException(status_code=400, detail="Invalid music url")
        
        post_data = post.dict()
        post_data["publisher_id"] = user_id
        post_data["posted_at"] = datetime.now()
        post_data["likes"] = [] 
        post_data["comments"] = []
        post_data["hashtags"] = post.hashtags or []
        valid_tagged_users = []
        for username in post.tagged_users:
            try:
                user = await get_user_by_username(username)
                if user:
                    valid_tagged_users.append(user["_id"])
                else:
                    print(f"User with username {username} not found.")
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid tagged user: {username}")
        
        post_data["tagged_users"] = valid_tagged_users


        new_post = await create_post(post_data)
        return {"message": "Post created successfully.", "post": new_post}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")