from fastapi import APIRouter, HTTPException
from app.services.auth_service import authenticate_user
from app.utils.auth import verify_token
from app.models.pydantic import LoginRequest, VerifyTokenRequest

router = APIRouter()


@router.post("/login")
async def login(data: LoginRequest):

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
