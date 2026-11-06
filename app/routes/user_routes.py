from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user
from app.models.pydantic import UserUpdateRequest
from app.utils.user_validator import validate_email, validate_username, validate_string_length, validate_password
from app.services.user_service import (
    get_user_by_email,
    get_user_by_username,
    update_user,
    follow_user,
    unfollow_user,
    get_followers,
    get_following,
)

router = APIRouter()


@router.get("/get-by-email")
async def get_user_by_email_route(email: str, _: dict = Depends(get_current_user)):
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.pop("password", None)
    return {"user": user}


@router.get("/profile/{username}")
async def get_user_profile(username: str):
    user = await get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.pop("password", None)
    return {"user_profile": user}


@router.put("/profile/update")
async def update_user_profile(
    data: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update.")
    if "full_name" in update_data and not validate_string_length(update_data["full_name"], min_len=1, max_len=100):
        raise HTTPException(status_code=400, detail="Full name must be between 1 and 100 characters.")
    if "password" in update_data and not validate_password(update_data["password"]):
        raise HTTPException(status_code=400, detail="Invalid password format.")
    if "username" in update_data and not validate_username(update_data["username"]):
        raise HTTPException(status_code=400, detail="Invalid username format.")
    if "email" in update_data and not validate_email(update_data["email"]):
        raise HTTPException(status_code=400, detail="Invalid email format.")

    try:
        updated_user = await update_user(current_user["_id"], update_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found.")
    updated_user.pop("password", None)
    return {"message": "Profile updated.", "user": updated_user}


@router.post("/follow/{username}")
async def follow_user_by_username(username: str, current_user: dict = Depends(get_current_user)):
    target = await get_user_by_username(username)
    if not target:
        raise HTTPException(status_code=404, detail="User not found.")
    try:
        await follow_user(current_user["_id"], target["_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": f"Now following {username}."}


@router.post("/unfollow/{username}")
async def unfollow_user_by_username(username: str, current_user: dict = Depends(get_current_user)):
    target = await get_user_by_username(username)
    if not target:
        raise HTTPException(status_code=404, detail="User not found.")
    try:
        await unfollow_user(current_user["_id"], target["_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": f"Unfollowed {username}."}


@router.get("/{user_id}/followers")
async def get_followers_route(user_id: str):
    try:
        followers = await get_followers(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"followers": followers}


@router.get("/{user_id}/following")
async def get_following_route(user_id: str):
    try:
        following = await get_following(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"following": following}
