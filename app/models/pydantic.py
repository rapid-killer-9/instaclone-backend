from pydantic import BaseModel, Field, root_validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class PostCategory(str, Enum):
    tech = "Tech"
    entertainment = "Entertainment"
    business = "Business"
    sports = "Sports"
    music = "Music"
    art = "Art"
    education = "Education"


class Comment(BaseModel):
    user_id: str  
    text: str  
    created_at: datetime 


class User(BaseModel):
    username: str 
    email: str  
    password: str  
    full_name: Optional[str] = None  

    @property
    def followers_count(self):
        return len(self.followers)  

    @property
    def following_count(self):
        return len(self.following) 

    @property
    def posts_count(self):
        return len(self.posts) 


class UpdateUserProfileRequest(BaseModel):
    user_id: str
    update_data: Dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="Fields to update, allowing only 'full_name', 'username' and 'email'."
    )

    @root_validator(pre=True)
    def validate_update_data(cls, values):
        update_data = values.get('update_data', {})
        allowed_keys = {"full_name", "username", "email"}
        for key in update_data.keys():
            if key not in allowed_keys:
                raise ValueError(f"Invalid key '{key}'. Only 'full_name', 'username' and 'email'  are allowed.")
        return values


class LoginRequest(BaseModel):
    email: str
    password: str

class VerifyTokenRequest(BaseModel):
    token: str


class Post(BaseModel):
    caption: str  
    media_url: str  
    music_url: Optional[str] = None  
    category: PostCategory 
    posted_at: datetime
    publisher_id: str  
    likes: Optional[List[str]] = Field(default_factory=list)  
    comments: Optional[List[str]] = Field(default_factory=list)  
    description: Optional[str] = None
    hashtags: Optional[List[str]] = Field(default_factory=list)  

    @property
    def likes_count(self):
        return len(self.likes)  

    @property
    def comments_count(self):
        return len(self.comments) 
