import re
from typing import List

def validate_caption(caption: str, max_len: int = 100) -> bool:
    return len(caption) <= max_len and bool(caption.strip())

def validate_description(description: str, max_len: int = 500) -> bool:
    return len(description) <= max_len

def validate_hashtags(hashtags: List[str], max_len: int = 20, max_count: int = 10) -> bool:
    if len(hashtags) > max_count:
        return False
    for tag in hashtags:
        if len(tag) > max_len:
            return False
    return True

def validate_media_url(media_url: str) -> bool:
    regex = r'^(http|https)://'
    return re.match(regex, media_url) is not None

def validate_music_url(music_url: str) -> bool:
    regex = r'^(http|https)://'
    return re.match(regex, music_url) is not None

def validate_category(category: str) -> bool:
    return category in ["Tech", "Entertainment", "Business", "Sports", "Music", "Art", "Education"]