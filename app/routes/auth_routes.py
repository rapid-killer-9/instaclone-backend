from fastapi import APIRouter, HTTPException, Request
from app.services.auth_service import authenticate_user, create_user
from app.utils.auth import verify_token
from app.utils.rate_limit import limiter
from app.models.pydantic import UserCreateRequest, UserLoginRequest, VerifyTokenRequest
from app.utils.user_validator import validate_username, validate_string_length, validate_password

router = APIRouter()


@router.post("/create", status_code=201)
@limiter.limit("10/minute")
async def create_new_user(request: Request, user: UserCreateRequest):
    if not validate_username(user.username):
        raise HTTPException(status_code=400, detail="Username must be 3–30 characters and contain only letters, digits, underscores, or hyphens.")
    if not validate_string_length(user.full_name, min_len=1, max_len=100):
        raise HTTPException(status_code=400, detail="Full name must be between 1 and 100 characters.")
    if not validate_password(user.password):
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters and contain an uppercase letter, a lowercase letter, a digit, and a special character.")

    try:
        user_data = await create_user(user.email, user.password, user.full_name, user.username)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return {"message": "User created successfully.", "user": user_data}


@router.post("/login")
@limiter.limit("20/minute")
async def login(request: Request, data: UserLoginRequest):
    token = await authenticate_user(data.email, data.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    return {"access_token": token, "token_type": "bearer"}


@router.post("/verify-token")
async def verify_token_route(data: VerifyTokenRequest):
    payload = verify_token(data.token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    return {"message": "Token is valid.", "user_id": payload.get("user_id")}
