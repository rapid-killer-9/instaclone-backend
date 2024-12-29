from pydantic import BaseModel, Field
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
    profile_picture: Optional[str] = None
    posts: Optional[List[str]] = Field(default_factory=list) 
    followers: Optional[List[str]] = Field(default_factory=list) 
    following: Optional[List[str]] = Field(default_factory=list) 

    @property
    def followers_count(self):
        return len(self.followers)  

    @property
    def following_count(self):
        return len(self.following) 

    @property
    def posts_count(self):
        return len(self.posts) 


class GetUserByEmailRequest(BaseModel):
    email: str

class GetUserProfileRequest(BaseModel):
    username: str

class UpdateUserProfileRequest(BaseModel):
    user_id: str
    update_data: Dict

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
