"""
User edge cases: profile update validation, social graph consistency, and pagination.
"""
import pytest

from tests.conftest import USER_A, USER_B


# ── profile update — username validation ──────────────────────────────────────

async def test_update_username_to_min_length(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"username": "xyz"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["user"]["username"] == "xyz"


async def test_update_username_too_short_rejected(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"username": "ab"}, headers=auth_headers)
    assert resp.status_code == 400


async def test_update_username_too_long_rejected(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"username": "a" * 31}, headers=auth_headers)
    assert resp.status_code == 400


async def test_update_username_special_char_rejected(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"username": "alice@bad"}, headers=auth_headers)
    assert resp.status_code == 400


async def test_update_username_hyphen_allowed(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"username": "alice-new"}, headers=auth_headers)
    assert resp.status_code == 200


# ── profile update — full_name boundaries ────────────────────────────────────

async def test_update_full_name_at_max_length(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"full_name": "A" * 100}, headers=auth_headers)
    assert resp.status_code == 200


async def test_update_full_name_over_max_length_rejected(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"full_name": "A" * 101}, headers=auth_headers)
    assert resp.status_code == 400


async def test_update_full_name_empty_rejected(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"full_name": ""}, headers=auth_headers)
    assert resp.status_code == 400


# ── profile update — password validation ─────────────────────────────────────

async def test_update_password_weak_rejected(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"password": "simple"}, headers=auth_headers)
    assert resp.status_code == 400


async def test_update_password_strong_accepted(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"password": "NewPass1!"}, headers=auth_headers)
    assert resp.status_code == 200


async def test_update_password_allows_new_login(client, auth_headers):
    new_password = "NewPass1!"
    await client.put("/users/profile/update", json={"password": new_password}, headers=auth_headers)
    login_resp = await client.post("/auth/login", json={"email": USER_A["email"], "password": new_password})
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()


# ── profile update — email validation ────────────────────────────────────────

async def test_update_email_invalid_format_rejected(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"email": "not-an-email"}, headers=auth_headers)
    assert resp.status_code == 422


async def test_update_email_valid_accepted(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"email": "alice_updated@example.com"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["user"]["email"] == "alice_updated@example.com"


# ── social graph — follow / unfollow cycles ───────────────────────────────────

async def test_follow_unfollow_cycle(client, auth_headers, second_auth_headers):
    r1 = await client.post(f"/users/follow/{USER_B['username']}", headers=auth_headers)
    assert r1.status_code == 200

    r2 = await client.post(f"/users/unfollow/{USER_B['username']}", headers=auth_headers)
    assert r2.status_code == 200

    r3 = await client.post(f"/users/follow/{USER_B['username']}", headers=auth_headers)
    assert r3.status_code == 200


async def test_mutual_follow(client, auth_headers, second_auth_headers):
    await client.post(f"/users/follow/{USER_B['username']}", headers=auth_headers)
    await client.post(f"/users/follow/{USER_A['username']}", headers=second_auth_headers)

    alice_profile = (await client.get(f"/users/profile/{USER_A['username']}")).json()["user_profile"]
    bob_profile = (await client.get(f"/users/profile/{USER_B['username']}")).json()["user_profile"]
    alice_id = alice_profile["_id"]
    bob_id = bob_profile["_id"]

    alice_followers = (await client.get(f"/users/{alice_id}/followers")).json()["followers"]
    bob_followers = (await client.get(f"/users/{bob_id}/followers")).json()["followers"]

    assert any(f["username"] == USER_B["username"] for f in alice_followers)
    assert any(f["username"] == USER_A["username"] for f in bob_followers)


async def test_unfollow_nonexistent_user_rejected(client, auth_headers):
    resp = await client.post("/users/unfollow/ghost", headers=auth_headers)
    assert resp.status_code == 404


async def test_follow_nonexistent_user_rejected(client, auth_headers):
    resp = await client.post("/users/follow/ghost", headers=auth_headers)
    assert resp.status_code == 404


async def test_follow_self_rejected(client, auth_headers):
    resp = await client.post(f"/users/follow/{USER_A['username']}", headers=auth_headers)
    assert resp.status_code == 400


async def test_unfollow_self_rejected(client, auth_headers):
    resp = await client.post(f"/users/unfollow/{USER_A['username']}", headers=auth_headers)
    assert resp.status_code == 400


# ── followers / following list edge cases ────────────────────────────────────

async def test_get_followers_when_none(client, auth_headers):
    profile = (await client.get(f"/users/profile/{USER_A['username']}")).json()["user_profile"]
    resp = await client.get(f"/users/{profile['_id']}/followers")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
    assert resp.json()["followers"] == []


async def test_get_following_when_none(client, auth_headers):
    profile = (await client.get(f"/users/profile/{USER_A['username']}")).json()["user_profile"]
    resp = await client.get(f"/users/{profile['_id']}/following")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
    assert resp.json()["following"] == []


async def test_followers_pagination_beyond_total_returns_empty(client, auth_headers, second_auth_headers):
    await client.post(f"/users/follow/{USER_A['username']}", headers=second_auth_headers)
    profile = (await client.get(f"/users/profile/{USER_A['username']}")).json()["user_profile"]
    resp = await client.get(f"/users/{profile['_id']}/followers", params={"page": 999, "limit": 20})
    assert resp.status_code == 200
    assert resp.json()["followers"] == []


async def test_following_list_reflects_follows(client, auth_headers, second_auth_headers):
    await client.post(f"/users/follow/{USER_B['username']}", headers=auth_headers)
    profile = (await client.get(f"/users/profile/{USER_A['username']}")).json()["user_profile"]
    resp = await client.get(f"/users/{profile['_id']}/following")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert resp.json()["following"][0]["username"] == USER_B["username"]


async def test_following_list_updates_after_unfollow(client, auth_headers, second_auth_headers):
    await client.post(f"/users/follow/{USER_B['username']}", headers=auth_headers)
    await client.post(f"/users/unfollow/{USER_B['username']}", headers=auth_headers)
    profile = (await client.get(f"/users/profile/{USER_A['username']}")).json()["user_profile"]
    resp = await client.get(f"/users/{profile['_id']}/following")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


async def test_followers_invalid_user_id(client):
    resp = await client.get("/users/not-an-objectid/followers")
    assert resp.status_code == 400


async def test_following_invalid_user_id(client):
    resp = await client.get("/users/not-an-objectid/following")
    assert resp.status_code == 400


async def test_followers_nonexistent_user_id(client):
    # Service raises ValueError for unknown users, route maps that to 400
    resp = await client.get("/users/000000000000000000000000/followers")
    assert resp.status_code == 400


async def test_following_nonexistent_user_id(client):
    resp = await client.get("/users/000000000000000000000000/following")
    assert resp.status_code == 400


# ── get-by-email ──────────────────────────────────────────────────────────────

async def test_get_by_email_unauthenticated(client, auth_headers):
    resp = await client.get("/users/get-by-email", params={"email": USER_A["email"]})
    assert resp.status_code == 401


async def test_get_by_email_invalid_format(client, auth_headers):
    # No email-format validation at the route level; returns 404 when no user is found
    resp = await client.get("/users/get-by-email", params={"email": "not-an-email"}, headers=auth_headers)
    assert resp.status_code == 404


# ── profile response — sensitive field exclusion ──────────────────────────────

async def test_public_profile_hides_password(client, auth_headers):
    resp = await client.get(f"/users/profile/{USER_A['username']}")
    assert resp.status_code == 200
    assert "password" not in resp.json()["user_profile"]


async def test_me_endpoint_hides_password(client, auth_headers):
    resp = await client.get("/users/me", headers=auth_headers)
    assert resp.status_code == 200
    assert "password" not in resp.json()["user"]


async def test_get_by_email_hides_password(client, auth_headers):
    resp = await client.get("/users/get-by-email", params={"email": USER_A["email"]}, headers=auth_headers)
    assert resp.status_code == 200
    assert "password" not in resp.json()["user"]


# ── security — profile update field injection ─────────────────────────────────

async def test_update_unknown_field_rejected(client, auth_headers):
    """Unknown fields must be rejected with 422, not silently ignored."""
    resp = await client.put("/users/profile/update", json={"is_admin": True}, headers=auth_headers)
    assert resp.status_code == 422


async def test_update_posts_field_injection_rejected(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"posts": ["fake-post-id"]}, headers=auth_headers)
    assert resp.status_code == 422


async def test_update_followers_field_injection_rejected(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"followers": ["attacker-id"]}, headers=auth_headers)
    assert resp.status_code == 422
