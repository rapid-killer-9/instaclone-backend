import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("MONGO_URI")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
