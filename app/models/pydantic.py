from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    username: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyTokenRequest(BaseModel):
    token: str

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class PostCategory(str, Enum):
    tech = "Tech"
    entertainment = "Entertainment"
    business = "Business"
    sports = "Sports"
    music = "Music"
    art = "Art"
    education = "Education"

class PostCreateRequest(BaseModel):
    category: PostCategory 
    caption: str  
    description: str
    media_url: str
    music_url: Optional[str] = None  
    hashtags: Optional[List[str]] = Field(default_factory=list) 
    tagged_users: Optional[List[str]] = Field(default_factory=list)

class CommentCreateRequest(BaseModel):
    user_id: str  
    text: str  

