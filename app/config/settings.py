import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

_missing = [name for name, val in [
    ("MONGO_URI", DATABASE_URL),
    ("JWT_SECRET_KEY", SECRET_KEY),
] if not val]

if _missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(_missing)}")
