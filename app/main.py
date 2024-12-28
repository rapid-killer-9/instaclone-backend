from dotenv import load_dotenv
from fastapi import FastAPI
import os

app = FastAPI()
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Instagram Clone Backend!"}