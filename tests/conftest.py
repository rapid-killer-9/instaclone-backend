import os

# Must be set before any app module is imported so settings.py picks them up
os.environ["MONGO_URI"] = "mongodb://localhost:27017/instaclone_test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["JWT_ALGORITHM"] = "HS256"

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.utils.db import init_db, close_db, get_database
from app.utils.rate_limit import limiter

USER_A = {
    "email": "alice@example.com",
    "password": "AlicePass1!",
    "full_name": "Alice Smith",
    "username": "alice",
}

USER_B = {
    "email": "bob@example.com",
    "password": "BobPass1!",
    "full_name": "Bob Jones",
    "username": "bob",
}

VALID_POST = {
    "category": "Tech",
    "caption": "Hello world",
    "description": "My first post",
    "media_url": "https://example.com/image.jpg",
}


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Clear the in-memory rate limiter between tests so limits never spill over."""
    try:
        limiter._storage.reset()
    except AttributeError:
        pass


@pytest_asyncio.fixture
async def client():
    # Create a fresh Motor client bound to this test's event loop.
    # ASGITransport does not trigger the ASGI lifespan, so we do this manually.
    init_db(os.environ["MONGO_URI"])
    db = get_database()
    await db.users.drop()
    await db.posts.drop()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c
    finally:
        close_db()


@pytest_asyncio.fixture
async def auth_headers(client):
    resp = await client.post("/auth/create", json=USER_A)
    assert resp.status_code == 201
    token = resp.json()["user"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def second_auth_headers(client):
    resp = await client.post("/auth/create", json=USER_B)
    assert resp.status_code == 201
    token = resp.json()["user"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
