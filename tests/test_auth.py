import pytest
from tests.conftest import USER_A


async def test_register_success(client):
    resp = await client.post("/auth/create", json=USER_A)
    assert resp.status_code == 201
    body = resp.json()
    assert body["user"]["email"] == USER_A["email"]
    assert body["user"]["username"] == USER_A["username"]
    assert "access_token" in body["user"]
    assert "password" not in body["user"]


async def test_register_duplicate_email(client):
    await client.post("/auth/create", json=USER_A)
    duplicate = {**USER_A, "username": "alice2"}
    resp = await client.post("/auth/create", json=duplicate)
    assert resp.status_code == 409
    assert "Email" in resp.json()["detail"]


async def test_register_duplicate_username(client):
    await client.post("/auth/create", json=USER_A)
    duplicate = {**USER_A, "email": "other@example.com"}
    resp = await client.post("/auth/create", json=duplicate)
    assert resp.status_code == 409
    assert "Username" in resp.json()["detail"]


async def test_register_weak_password(client):
    resp = await client.post("/auth/create", json={**USER_A, "password": "simple"})
    assert resp.status_code == 400


async def test_register_invalid_email(client):
    resp = await client.post("/auth/create", json={**USER_A, "email": "not-an-email"})
    assert resp.status_code == 422


async def test_register_short_username(client):
    resp = await client.post("/auth/create", json={**USER_A, "username": "ab"})
    assert resp.status_code == 400


async def test_login_success(client):
    await client.post("/auth/create", json=USER_A)
    resp = await client.post("/auth/login", json={"email": USER_A["email"], "password": USER_A["password"]})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(client):
    await client.post("/auth/create", json=USER_A)
    resp = await client.post("/auth/login", json={"email": USER_A["email"], "password": "WrongPass1!"})
    assert resp.status_code == 401


async def test_login_nonexistent_user(client):
    resp = await client.post("/auth/login", json={"email": "ghost@example.com", "password": "Pass1234!"})
    assert resp.status_code == 401


async def test_verify_token_valid(client):
    await client.post("/auth/create", json=USER_A)
    login_resp = await client.post("/auth/login", json={"email": USER_A["email"], "password": USER_A["password"]})
    token = login_resp.json()["access_token"]

    resp = await client.post("/auth/verify-token", json={"token": token})
    assert resp.status_code == 200
    assert resp.json()["message"] == "Token is valid."


async def test_verify_token_invalid(client):
    resp = await client.post("/auth/verify-token", json={"token": "this.is.garbage"})
    assert resp.status_code == 401
