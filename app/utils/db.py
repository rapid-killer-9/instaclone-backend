from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import DATABASE_URL
from bson import ObjectId

async def get_database():
    client = AsyncIOMotorClient(DATABASE_URL)
    return client.get_database()


