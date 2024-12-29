import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
