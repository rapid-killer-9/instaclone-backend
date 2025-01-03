from fastapi import APIRouter, HTTPException
from app.services.auth_service import authenticate_user, create_user
from app.utils.auth import verify_token
from app.models.pydantic import UserCreateRequest, UserLoginRequest, VerifyTokenRequest
from app.utils.user_validator import validate_email, validate_username, validate_string_length, validate_password

router = APIRouter()

@router.post("/create")
async def create_new_user(user: UserCreateRequest):
    try:
        if not validate_email(user.email):
            raise HTTPException(status_code=400, detail="Invalid email.")
        if not validate_username(user.username):
            raise HTTPException(status_code=400, detail="Invalid username.")
        if not validate_string_length(user.full_name, min_len=1, max_len=100):
            raise HTTPException(status_code=400, detail="Full name length must be between 1 and 100 characters.")
        if not validate_password(user.password):
            raise HTTPException(status_code=400, detail="Invalid password. Password must contain at least one uppercase letter, one lowercase letter, one digit, one special character, and be at least 8 characters long.")
        
        user_data = await create_user(user.email, user.password, user.full_name, user.username)
        return {"message": "User created successfully.", "user": user_data}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(data: UserLoginRequest):

    token = await authenticate_user(data.email, data.password)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token}


@router.post("/verify-token")
async def verify_token_route(data: VerifyTokenRequest):

    payload = verify_token(data.token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"message": "Token is valid", "user_id": payload.get("user_id")}
