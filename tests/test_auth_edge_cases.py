"""
Auth edge cases: validation boundaries, token security, and request-format checks.
"""
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from tests.conftest import USER_A


# ── registration — password boundaries ───────────────────────────────────────

async def test_register_password_exactly_8_chars(client):
    resp = await client.post("/auth/create", json={**USER_A, "password": "Abcdef1!"})
    assert resp.status_code == 201


async def test_register_password_7_chars_rejected(client):
    resp = await client.post("/auth/create", json={**USER_A, "password": "Abcde1!"})
    assert resp.status_code == 400


async def test_register_password_missing_uppercase(client):
    resp = await client.post("/auth/create", json={**USER_A, "password": "abcdef1!"})
    assert resp.status_code == 400


async def test_register_password_missing_lowercase(client):
    resp = await client.post("/auth/create", json={**USER_A, "password": "ABCDEF1!"})
    assert resp.status_code == 400


async def test_register_password_missing_digit(client):
    resp = await client.post("/auth/create", json={**USER_A, "password": "Abcdefg!"})
    assert resp.status_code == 400


async def test_register_password_missing_special_char(client):
    resp = await client.post("/auth/create", json={**USER_A, "password": "Abcdef12"})
    assert resp.status_code == 400


# ── registration — username boundaries ───────────────────────────────────────

async def test_register_username_min_length(client):
    resp = await client.post("/auth/create", json={**USER_A, "username": "abc"})
    assert resp.status_code == 201


async def test_register_username_max_length(client):
    resp = await client.post("/auth/create", json={**USER_A, "username": "a" * 30})
    assert resp.status_code == 201


async def test_register_username_too_short(client):
    resp = await client.post("/auth/create", json={**USER_A, "username": "ab"})
    assert resp.status_code == 400


async def test_register_username_too_long(client):
    resp = await client.post("/auth/create", json={**USER_A, "username": "a" * 31})
    assert resp.status_code == 400


async def test_register_username_with_space_rejected(client):
    resp = await client.post("/auth/create", json={**USER_A, "username": "alice bob"})
    assert resp.status_code == 400


async def test_register_username_with_at_sign_rejected(client):
    resp = await client.post("/auth/create", json={**USER_A, "username": "alice@b"})
    assert resp.status_code == 400


async def test_register_username_hyphen_and_underscore_allowed(client):
    resp = await client.post("/auth/create", json={**USER_A, "username": "alice_b-c"})
    assert resp.status_code == 201


# ── registration — full_name boundaries ──────────────────────────────────────

async def test_register_full_name_min_length(client):
    resp = await client.post("/auth/create", json={**USER_A, "full_name": "A"})
    assert resp.status_code == 201


async def test_register_full_name_max_length(client):
    resp = await client.post("/auth/create", json={**USER_A, "full_name": "A" * 100})
    assert resp.status_code == 201


async def test_register_full_name_over_max_length(client):
    resp = await client.post("/auth/create", json={**USER_A, "full_name": "A" * 101})
    assert resp.status_code == 400


async def test_register_full_name_empty_rejected(client):
    resp = await client.post("/auth/create", json={**USER_A, "full_name": ""})
    assert resp.status_code == 400


# ── registration — missing / malformed body ───────────────────────────────────

async def test_register_missing_all_fields(client):
    resp = await client.post("/auth/create", json={})
    assert resp.status_code == 422


async def test_register_missing_email(client):
    body = {k: v for k, v in USER_A.items() if k != "email"}
    resp = await client.post("/auth/create", json=body)
    assert resp.status_code == 422


async def test_register_missing_password(client):
    body = {k: v for k, v in USER_A.items() if k != "password"}
    resp = await client.post("/auth/create", json=body)
    assert resp.status_code == 422


async def test_register_invalid_email_format(client):
    resp = await client.post("/auth/create", json={**USER_A, "email": "not-an-email"})
    assert resp.status_code == 422


async def test_register_email_without_tld(client):
    resp = await client.post("/auth/create", json={**USER_A, "email": "alice@example"})
    assert resp.status_code == 422


# ── login edge cases ──────────────────────────────────────────────────────────

async def test_login_missing_password_field(client):
    await client.post("/auth/create", json=USER_A)
    resp = await client.post("/auth/login", json={"email": USER_A["email"]})
    assert resp.status_code == 422


async def test_login_missing_email_field(client):
    await client.post("/auth/create", json=USER_A)
    resp = await client.post("/auth/login", json={"password": USER_A["password"]})
    assert resp.status_code == 422


async def test_login_empty_body(client):
    resp = await client.post("/auth/login", json={})
    assert resp.status_code == 422


async def test_login_extra_fields_ignored(client):
    await client.post("/auth/create", json=USER_A)
    resp = await client.post("/auth/login", json={
        "email": USER_A["email"],
        "password": USER_A["password"],
        "extra_field": "should-be-ignored",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


# ── authorization header format ───────────────────────────────────────────────

async def test_auth_header_no_authorization(client, auth_headers):
    resp = await client.get("/users/me")
    assert resp.status_code == 401


async def test_auth_header_wrong_scheme(client, auth_headers):
    token = auth_headers["Authorization"].split(" ")[1]
    resp = await client.get("/users/me", headers={"Authorization": f"Token {token}"})
    assert resp.status_code == 401


async def test_auth_header_missing_token_part(client):
    resp = await client.get("/users/me", headers={"Authorization": "Bearer"})
    assert resp.status_code == 401


async def test_auth_header_empty_token(client):
    resp = await client.get("/users/me", headers={"Authorization": "Bearer "})
    assert resp.status_code == 401


async def test_auth_header_lowercase_bearer_accepted(client, auth_headers):
    token = auth_headers["Authorization"].split(" ")[1]
    resp = await client.get("/users/me", headers={"Authorization": f"bearer {token}"})
    assert resp.status_code == 200


# ── JWT security ──────────────────────────────────────────────────────────────

async def test_tampered_token_rejected(client, auth_headers):
    """Token re-signed with a different key must be rejected."""
    payload = {
        "email": USER_A["email"],
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
    }
    forged = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")
    resp = await client.get("/users/me", headers={"Authorization": f"Bearer {forged}"})
    assert resp.status_code == 401


async def test_expired_token_rejected(client):
    """Tokens with a past expiry must be rejected."""
    await client.post("/auth/create", json=USER_A)
    payload = {
        "email": USER_A["email"],
        "exp": datetime.now(tz=timezone.utc) - timedelta(seconds=1),
    }
    expired = jwt.encode(payload, "test-secret-key-not-for-production", algorithm="HS256")
    resp = await client.get("/users/me", headers={"Authorization": f"Bearer {expired}"})
    assert resp.status_code == 401


async def test_token_with_nonexistent_user_rejected(client):
    """Token that passes signature check but references an email not in the DB must be rejected."""
    payload = {
        "email": "ghost-never-registered@example.com",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
    }
    token = jwt.encode(payload, "test-secret-key-not-for-production", algorithm="HS256")
    resp = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


async def test_token_missing_email_claim(client):
    """Token without an email claim must be rejected."""
    payload = {
        "user_id": "some-id",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
    }
    token = jwt.encode(payload, "test-secret-key-not-for-production", algorithm="HS256")
    resp = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


async def test_garbage_token_rejected(client):
    resp = await client.get("/users/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert resp.status_code == 401


# ── verify-token endpoint ─────────────────────────────────────────────────────

async def test_verify_token_empty_string(client):
    resp = await client.post("/auth/verify-token", json={"token": ""})
    assert resp.status_code == 401


async def test_verify_token_missing_field(client):
    resp = await client.post("/auth/verify-token", json={})
    assert resp.status_code == 422


# ── token refresh ─────────────────────────────────────────────────────────────

async def test_refresh_token_returns_new_token(client, auth_headers):
    resp = await client.post("/auth/refresh", headers=auth_headers)
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    assert resp.json()["token_type"] == "bearer"


async def test_refresh_token_new_token_authenticates(client, auth_headers):
    new_token = (await client.post("/auth/refresh", headers=auth_headers)).json()["access_token"]
    me_resp = await client.get("/users/me", headers={"Authorization": f"Bearer {new_token}"})
    assert me_resp.status_code == 200


async def test_refresh_token_unauthenticated_rejected(client):
    resp = await client.post("/auth/refresh")
    assert resp.status_code == 401
