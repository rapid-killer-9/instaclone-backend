from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import DATABASE_URL

async def get_database():
    client = AsyncIOMotorClient(DATABASE_URL)
    return client.get_database()

def serialize_document(document):
    if not document:
        return None
    document["_id"] = str(document["_id"])
    return document