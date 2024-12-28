import re
from datetime import datetime
from bson import ObjectId


def validate_email(email: str) -> bool:
    """
    Validate an email address using regex.
    """
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$'
    return re.match(regex, email) is not None


def validate_password(password: str) -> bool:
    """
    Validate the strength of the password.
    Password must contain at least one uppercase letter, one lowercase letter, one digit, and be at least 8 characters long.
    """
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
    return True


def validate_username(username: str) -> bool:
    """
    Validate a username that contains only letters, numbers, hyphens, and underscores.
    """
    regex = r'^[A-Za-z0-9_-]{3,30}$'  # 3 to 30 characters, can contain letters, digits, hyphens, and underscores
    return re.match(regex, username) is not None


def validate_string_length(string: str, min_len: int = 1, max_len: int = 255) -> bool:
    """
    Validate that a string has a length between `min_len` and `max_len` (inclusive).
    """
    return min_len <= len(string) <= max_len


def validate_date(date_string: str) -> bool:
    """
    Validate if a string is a valid date in the format YYYY-MM-DD.
    """
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_object_id(id_string: str) -> bool:
    """
    Validate if the string is a valid MongoDB ObjectId.
    """
    try:
        ObjectId(id_string)
        return True
    except Exception:
        return False
