from typing import Optional, List
from bson import ObjectId


class UserDB:
    def __init__(self, email: str, password: str, full_name: Optional[str], username: str,
                 posts: Optional[List[str]] = None, followers: Optional[List[str]] = None,
                 following: Optional[List[str]] = None):
        self.email = email
        self.password = password
        self.full_name = full_name
        self.username = username
        self.posts = posts or []
        self.tagged_posts = []
        self.followers = followers or []
        self.following = following or []

    def to_dict(self):
        return self.__dict__


class PostDB:
    def __init__(
        self, caption: str, media_url: str, category: str,
        posted_at, publisher_id: str, description: str,
        music_url: Optional[str] = None, likes: Optional[List[str]] = None,
        comments: Optional[List] = None, hashtags: Optional[List[str]] = None,
        tagged_users: Optional[List[str]] = None,
    ):
        self.category = category
        self.caption = caption
        self.description = description
        self.media_url = media_url
        self.posted_at = posted_at
        self.publisher_id = publisher_id
        self.music_url = music_url
        self.likes = likes or []
        self.comments = comments or []
        self.hashtags = hashtags or []
        self.tagged_users = tagged_users or []

    def to_dict(self):
        return self.__dict__


def serialize_document(document):
    if document is None:
        return None
    if isinstance(document, ObjectId):
        return str(document)
    if isinstance(document, dict):
        return {key: serialize_document(value) for key, value in document.items()}
    if isinstance(document, list):
        return [serialize_document(item) for item in document]
    return document
