import re
from datetime import datetime
from bson import ObjectId


def validate_email(email: str) -> bool:
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$'
    return re.match(regex, email) is not None


def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r'[A-Za-z]', password):  # checks for letters
        return False
    if not re.search(r'\d', password):  # checks for digits
        return False
    if not re.search(r'[A-Z]', password):  # checks for uppercase letter
        return False
    if not re.search(r'[a-z]', password):  # checks for lowercase letter
        return False
    if not re.search(r'[^A-Za-z0-9]', password): # checks for special characters
        return False
    return True


def validate_username(username: str) -> bool:
    regex = r'^[A-Za-z0-9_-]{3,30}$'  
    return re.match(regex, username) is not None


def validate_string_length(string: str, min_len: int = 1, max_len: int = 255) -> bool:
    return min_len <= len(string) <= max_len

