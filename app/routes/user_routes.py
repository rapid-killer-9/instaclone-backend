from fastapi import APIRouter, HTTPException, Body, Depends
from app.utils.auth import get_current_user
from app.models.pydantic import UpdateUserProfileRequest
from app.utils.validator import validate_email, validate_username, validate_string_length
from app.services.user_service import (
    get_user_by_email, 
    get_user_by_username, 
    update_user, 
    follow_user, 
    unfollow_user, 
    get_followers, 
    get_following
)

router = APIRouter()

@router.get("/get-by-email")
async def get_user_by_email_route(email: str):
    try:
        user = await get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        user.pop("password", None)  
        return {"user": user}
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@router.get("/profile/{username}")
async def get_user_profile(username: str):
    try:
        user = await get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        user.pop("password", None)  # Use pop with default to avoid KeyError
        return {"user_profile": user}
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.put("/profile/update")
async def update_user_profile(data: UpdateUserProfileRequest):
    user_id = data.user_id  
    update_data = data.update_data
    try:
        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update.")
        if "password" in update_data:
            raise HTTPException(status_code=400, detail="Password cannot be updated.")
        if "full_name" in update_data and not validate_string_length(update_data["full_name"], min_len=1, max_len=100):
            raise HTTPException(status_code=400, detail="Full name length must be between 1 and 100 characters.")
        if "username" in update_data and not validate_username(update_data["username"]):
            raise HTTPException(status_code=400, detail="Invalid username format.")
        if "email" in update_data and not validate_email(update_data["email"]):
            raise HTTPException(status_code=400, detail="Invalid email format.")
        
        updated_user = await update_user(user_id, update_data)
        updated_user.pop("password")

        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found.")
        return {"message": "User profile updated.", "user": updated_user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@router.post("/follow/")
async def follow_user_route(target_user_id: str, current_user: str = Depends(get_current_user)):
    try:
        await follow_user(current_user["_id"], target_user_id)
        return {"message": "User followed successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.post("/follow/{username}")
async def follow_user_by_username(username: str, current_user: str = Depends(get_current_user)):
    try:
        target_user = await get_user_by_username(username)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found.")
        await follow_user(current_user["_id"], target_user["_id"])
        return {"message": "User followed successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@router.post("/unfollow/")
async def unfollow_user_route(target_user_id: str, current_user: str = Depends(get_current_user)):
    try:
        await unfollow_user(current_user["_id"], target_user_id)
        return {"message": "User unfollowed successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.post("/unfollow/{username}")
async def unfollow_user_by_username(username: str, current_user: str = Depends(get_current_user)):
    try:
        target_user = await get_user_by_username(username)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found.")
        await unfollow_user(current_user["_id"], target_user["_id"])
        return {"message": "User unfollowed successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@router.get("/{user_id}/followers")
async def get_followers_route(user_id: str):
    try:
        followers = await get_followers(user_id)
        return {"followers": followers}
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.get("/{user_id}/following")
async def get_following_route(user_id: str):
    try:
        following = await get_following(user_id)
        return {"following": following}
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")