import pytest
from tests.conftest import USER_A, USER_B


async def test_get_me(client, auth_headers):
    resp = await client.get("/users/me", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()["user"]
    assert body["email"] == USER_A["email"]
    assert "password" not in body


async def test_get_me_no_token(client):
    resp = await client.get("/users/me")
    assert resp.status_code == 401


async def test_get_me_invalid_token(client):
    resp = await client.get("/users/me", headers={"Authorization": "Bearer bad.token.here"})
    assert resp.status_code == 401


async def test_get_profile_by_username(client, auth_headers):
    resp = await client.get(f"/users/profile/{USER_A['username']}")
    assert resp.status_code == 200
    assert resp.json()["user_profile"]["username"] == USER_A["username"]
    assert "password" not in resp.json()["user_profile"]


async def test_get_profile_not_found(client):
    resp = await client.get("/users/profile/doesnotexist")
    assert resp.status_code == 404


async def test_get_user_by_email(client, auth_headers):
    resp = await client.get("/users/get-by-email", params={"email": USER_A["email"]}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["user"]["email"] == USER_A["email"]


async def test_get_user_by_email_not_found(client, auth_headers):
    resp = await client.get("/users/get-by-email", params={"email": "nobody@example.com"}, headers=auth_headers)
    assert resp.status_code == 404


async def test_update_profile_full_name(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"full_name": "Alice Updated"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["user"]["full_name"] == "Alice Updated"


async def test_update_profile_username(client, auth_headers):
    resp = await client.put("/users/profile/update", json={"username": "alice_new"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["user"]["username"] == "alice_new"


async def test_update_profile_duplicate_username(client, auth_headers, second_auth_headers):
    resp = await client.put("/users/profile/update", json={"username": USER_B["username"]}, headers=auth_headers)
    assert resp.status_code == 400
    assert "Username" in resp.json()["detail"]


async def test_update_profile_duplicate_email(client, auth_headers, second_auth_headers):
    resp = await client.put("/users/profile/update", json={"email": USER_B["email"]}, headers=auth_headers)
    assert resp.status_code == 400
    assert "Email" in resp.json()["detail"]


async def test_update_profile_no_fields(client, auth_headers):
    resp = await client.put("/users/profile/update", json={}, headers=auth_headers)
    assert resp.status_code == 400


async def test_follow_user(client, auth_headers, second_auth_headers):
    resp = await client.post(f"/users/follow/{USER_B['username']}", headers=auth_headers)
    assert resp.status_code == 200
    assert "following" in resp.json()["message"].lower()


async def test_follow_self(client, auth_headers):
    resp = await client.post(f"/users/follow/{USER_A['username']}", headers=auth_headers)
    assert resp.status_code == 400


async def test_follow_nonexistent_user(client, auth_headers):
    resp = await client.post("/users/follow/ghost", headers=auth_headers)
    assert resp.status_code == 404


async def test_follow_already_following(client, auth_headers, second_auth_headers):
    await client.post(f"/users/follow/{USER_B['username']}", headers=auth_headers)
    resp = await client.post(f"/users/follow/{USER_B['username']}", headers=auth_headers)
    assert resp.status_code == 400
    assert "Already following" in resp.json()["detail"]


async def test_unfollow_user(client, auth_headers, second_auth_headers):
    await client.post(f"/users/follow/{USER_B['username']}", headers=auth_headers)
    resp = await client.post(f"/users/unfollow/{USER_B['username']}", headers=auth_headers)
    assert resp.status_code == 200


async def test_unfollow_not_following(client, auth_headers, second_auth_headers):
    resp = await client.post(f"/users/unfollow/{USER_B['username']}", headers=auth_headers)
    assert resp.status_code == 400


async def test_get_followers(client, auth_headers, second_auth_headers):
    # Bob follows Alice
    await client.post(f"/users/follow/{USER_A['username']}", headers=second_auth_headers)

    # Get Alice's followers
    alice_profile = await client.get(f"/users/profile/{USER_A['username']}")
    alice_id = alice_profile.json()["user_profile"]["_id"]

    resp = await client.get(f"/users/{alice_id}/followers")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["followers"][0]["username"] == USER_B["username"]


async def test_get_following(client, auth_headers, second_auth_headers):
    # Alice follows Bob
    await client.post(f"/users/follow/{USER_B['username']}", headers=auth_headers)

    alice_profile = await client.get(f"/users/profile/{USER_A['username']}")
    alice_id = alice_profile.json()["user_profile"]["_id"]

    resp = await client.get(f"/users/{alice_id}/following")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["following"][0]["username"] == USER_B["username"]


async def test_get_followers_invalid_id(client):
    resp = await client.get("/users/not-a-valid-id/followers")
    assert resp.status_code == 400


async def test_followers_pagination(client, auth_headers, second_auth_headers):
    await client.post(f"/users/follow/{USER_A['username']}", headers=second_auth_headers)
    alice_profile = await client.get(f"/users/profile/{USER_A['username']}")
    alice_id = alice_profile.json()["user_profile"]["_id"]

    resp = await client.get(f"/users/{alice_id}/followers", params={"page": 1, "limit": 10})
    assert resp.status_code == 200
    assert resp.json()["limit"] == 10
    assert resp.json()["page"] == 1
