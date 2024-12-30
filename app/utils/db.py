from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import DATABASE_URL
from bson import ObjectId

async def get_database():
    client = AsyncIOMotorClient(DATABASE_URL)
    return client.get_database()

def serialize_document(document):
    """Recursively serialize MongoDB documents to be JSON-compatible."""
    if document is None:
        return None
    if isinstance(document, ObjectId):  # Convert single ObjectId to str
        return str(document)
    if isinstance(document, dict):  # Handle dictionaries
        return {key: serialize_document(value) for key, value in document.items()}
    if isinstance(document, list):  # Handle lists
        return [serialize_document(item) for item in document]
    return document 
