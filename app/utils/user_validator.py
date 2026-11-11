import re


def validate_email(email: str) -> bool:
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(regex, email) is not None


def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[^A-Za-z0-9]', password):
        return False
    return True


def validate_username(username: str) -> bool:
    regex = r'^[A-Za-z0-9_-]{3,30}$'
    return re.match(regex, username) is not None


def validate_string_length(string: str, min_len: int = 1, max_len: int = 255) -> bool:
    return min_len <= len(string) <= max_len
