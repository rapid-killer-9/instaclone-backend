from fastapi import APIRouter, HTTPException, Body
from app.services.user_service import create_user, get_user_by_email, get_user_by_username, update_user
from app.utils.validator import validate_email, validate_username, validate_string_length
from app.models.pydantic import User, GetUserByEmailRequest, GetUserProfileRequest, UpdateUserProfileRequest

router = APIRouter()

@router.post("/create")
async def create_new_user(user: User):
    try:
        if not validate_email(user.email):
            raise HTTPException(status_code=400, detail="Invalid email.")
        if not validate_username(user.username):
            raise HTTPException(status_code=400, detail="Invalid username.")
        
        user_data = await create_user(user.email, user.password, user.full_name, user.username)
        user_data.pop("password")
        return {"message": "User created successfully.", "user": user_data}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.post("/get-by-email")
async def get_user_by_email_route(data: GetUserByEmailRequest):
    email = data.email
    try:
        user = await get_user_by_email(email)
        user.pop("password")
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        return {"user": user}
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.post("/profile")
async def get_user_profile(data: GetUserProfileRequest):
    username = data.username
    try:
        user = await get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        user.pop("password")
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
        if "email" in update_data:
            raise HTTPException(status_code=400, detail="Email cannot be updated.")
        if "password" in update_data:
            raise HTTPException(status_code=400, detail="Password cannot be updated.")
        if "full_name" in update_data and not validate_string_length(update_data["full_name"], min_len=1, max_len=100):
            raise HTTPException(status_code=400, detail="Full name length must be between 1 and 100 characters.")
        if "name" in update_data and not validate_string_length(update_data["name"], min_len=1, max_len=100):
            raise HTTPException(status_code=400, detail="Name length must be between 1 and 100 characters.")
        if "username" in update_data and not validate_username(update_data["username"]):
            raise HTTPException(status_code=400, detail="Invalid username format.")
        
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
