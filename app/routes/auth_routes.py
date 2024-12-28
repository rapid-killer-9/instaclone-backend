from fastapi import APIRouter, HTTPException, Depends
from app.services.auth_service import authenticate_user, verify_user_token
from app.utils.auth import verify_token

router = APIRouter()

@router.post("/login")
async def login(email: str, password: str):
    token = await authenticate_user(email, password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token}

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully. Please remove your token from storage."}

@router.get("/verify-token")
async def verify_token_route(token: str):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"message": "Token is valid", "user_id": payload.get("user_id")}
