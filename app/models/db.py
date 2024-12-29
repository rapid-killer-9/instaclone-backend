# from pydantic import BaseModel, Field
from typing import Optional, List
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


class CommentDB:
    def __init__(self, user_id: str, text: str, created_at: datetime):
        self.user_id = user_id
        self.text = text
        self.created_at = created_at


class UserDB:
    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        profile_picture: Optional[str] = None,
        posts: Optional[List[str]] = None,
        followers: Optional[List[str]] = None,
        following: Optional[List[str]] = None,
    ):
        self.username = username
        self.email = email
        self.password = password
        self.full_name = full_name
        self.profile_picture = profile_picture
        self.posts = posts or []
        self.followers = followers or []
        self.following = following or []

    def to_dict(self):
        return self.__dict__


class PostDB:
    def __init__(
        self,
        caption: str,
        media_url: str,
        category: PostCategory,
        posted_at: datetime,
        publisher_id: str,
        music_url: Optional[str] = None,
        likes: Optional[List[str]] = None,
        comments: Optional[List[str]] = None,
        description: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
    ):
        self.caption = caption
        self.media_url = media_url
        self.category = category
        self.posted_at = posted_at
        self.publisher_id = publisher_id
        self.music_url = music_url
        self.likes = likes or []
        self.comments = comments or []
        self.description = description
        self.hashtags = hashtags or []

    def to_dict(self):
        return self.__dict__
