import pytest
from tests.conftest import USER_A, USER_B, VALID_POST


# ── helpers ──────────────────────────────────────────────────────────────────

async def create_post(client, headers, overrides=None):
    payload = {**VALID_POST, **(overrides or {})}
    resp = await client.post("/posts/", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()["post"]


# ── create ────────────────────────────────────────────────────────────────────

async def test_create_post_success(client, auth_headers):
    post = await create_post(client, auth_headers)
    assert post["caption"] == VALID_POST["caption"]
    assert post["category"] == VALID_POST["category"]
    assert "_id" in post


async def test_create_post_no_auth(client):
    resp = await client.post("/posts/", json=VALID_POST)
    assert resp.status_code == 401


async def test_create_post_caption_too_long(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "caption": "x" * 101}, headers=auth_headers)
    assert resp.status_code == 400


async def test_create_post_invalid_media_url(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "media_url": "not-a-url"}, headers=auth_headers)
    assert resp.status_code == 400


async def test_create_post_invalid_category(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "category": "InvalidCat"}, headers=auth_headers)
    assert resp.status_code == 422


async def test_create_post_too_many_hashtags(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "hashtags": ["tag"] * 11}, headers=auth_headers)
    assert resp.status_code == 400


async def test_create_post_tagged_user_not_found(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "tagged_users": ["ghost"]}, headers=auth_headers)
    assert resp.status_code == 400


# ── list & get ────────────────────────────────────────────────────────────────

async def test_list_posts_empty(client):
    resp = await client.get("/posts/")
    assert resp.status_code == 200
    assert resp.json()["posts"] == []


async def test_list_posts(client, auth_headers):
    await create_post(client, auth_headers)
    await create_post(client, auth_headers, {"caption": "Second post"})

    resp = await client.get("/posts/")
    assert resp.status_code == 200
    assert len(resp.json()["posts"]) == 2


async def test_list_posts_by_category(client, auth_headers):
    await create_post(client, auth_headers, {"category": "Tech"})
    await create_post(client, auth_headers, {"category": "Music"})

    resp = await client.get("/posts/", params={"category": "Tech"})
    assert resp.status_code == 200
    posts = resp.json()["posts"]
    assert all(p["category"] == "Tech" for p in posts)


async def test_list_posts_pagination(client, auth_headers):
    for i in range(5):
        await create_post(client, auth_headers, {"caption": f"Post {i}"})

    resp = await client.get("/posts/", params={"page": 1, "limit": 2})
    assert resp.status_code == 200
    assert len(resp.json()["posts"]) == 2
    assert resp.json()["limit"] == 2


async def test_get_post(client, auth_headers):
    post = await create_post(client, auth_headers)
    resp = await client.get(f"/posts/{post['_id']}")
    assert resp.status_code == 200
    assert resp.json()["post"]["_id"] == post["_id"]


async def test_get_post_not_found(client):
    resp = await client.get("/posts/000000000000000000000000")
    assert resp.status_code == 404


async def test_get_post_invalid_id(client):
    resp = await client.get("/posts/invalid-id")
    assert resp.status_code == 400


# ── delete ────────────────────────────────────────────────────────────────────

async def test_delete_post_by_owner(client, auth_headers):
    post = await create_post(client, auth_headers)
    resp = await client.delete(f"/posts/{post['_id']}", headers=auth_headers)
    assert resp.status_code == 204

    get_resp = await client.get(f"/posts/{post['_id']}")
    assert get_resp.status_code == 404


async def test_delete_post_not_owner(client, auth_headers, second_auth_headers):
    post = await create_post(client, auth_headers)
    resp = await client.delete(f"/posts/{post['_id']}", headers=second_auth_headers)
    assert resp.status_code == 403


async def test_delete_post_not_found(client, auth_headers):
    resp = await client.delete("/posts/000000000000000000000000", headers=auth_headers)
    assert resp.status_code == 404


# ── like / unlike ─────────────────────────────────────────────────────────────

async def test_like_post(client, auth_headers):
    post = await create_post(client, auth_headers)
    resp = await client.post(f"/posts/{post['_id']}/like", headers=auth_headers)
    assert resp.status_code == 200


async def test_like_post_already_liked(client, auth_headers):
    post = await create_post(client, auth_headers)
    await client.post(f"/posts/{post['_id']}/like", headers=auth_headers)
    resp = await client.post(f"/posts/{post['_id']}/like", headers=auth_headers)
    assert resp.status_code == 400
    assert "already liked" in resp.json()["detail"].lower()


async def test_unlike_post(client, auth_headers):
    post = await create_post(client, auth_headers)
    await client.post(f"/posts/{post['_id']}/like", headers=auth_headers)
    resp = await client.delete(f"/posts/{post['_id']}/like", headers=auth_headers)
    assert resp.status_code == 200


async def test_unlike_post_not_liked(client, auth_headers):
    post = await create_post(client, auth_headers)
    resp = await client.delete(f"/posts/{post['_id']}/like", headers=auth_headers)
    assert resp.status_code == 400


async def test_like_post_no_auth(client, auth_headers):
    post = await create_post(client, auth_headers)
    resp = await client.post(f"/posts/{post['_id']}/like")
    assert resp.status_code == 401


# ── comments ──────────────────────────────────────────────────────────────────

async def test_add_comment(client, auth_headers):
    post = await create_post(client, auth_headers)
    resp = await client.post(f"/posts/{post['_id']}/comments", json={"text": "Nice post!"}, headers=auth_headers)
    assert resp.status_code == 201
    comment = resp.json()["comment"]
    assert comment["text"] == "Nice post!"
    assert "_id" in comment


async def test_add_comment_empty_text(client, auth_headers):
    post = await create_post(client, auth_headers)
    resp = await client.post(f"/posts/{post['_id']}/comments", json={"text": ""}, headers=auth_headers)
    assert resp.status_code == 422


async def test_add_comment_no_auth(client, auth_headers):
    post = await create_post(client, auth_headers)
    resp = await client.post(f"/posts/{post['_id']}/comments", json={"text": "Hi"})
    assert resp.status_code == 401


async def test_add_comment_post_not_found(client, auth_headers):
    resp = await client.post("/posts/000000000000000000000000/comments", json={"text": "Hi"}, headers=auth_headers)
    assert resp.status_code == 400


# ── feed ──────────────────────────────────────────────────────────────────────

async def test_feed_shows_followed_posts(client, auth_headers, second_auth_headers):
    # Alice follows Bob
    await client.post(f"/users/follow/{USER_B['username']}", headers=auth_headers)
    # Bob creates a post
    await create_post(client, second_auth_headers, {"caption": "Bob's post"})

    resp = await client.get("/posts/feed", headers=auth_headers)
    assert resp.status_code == 200
    posts = resp.json()["posts"]
    assert len(posts) == 1
    assert posts[0]["caption"] == "Bob's post"


async def test_feed_excludes_non_followed_posts(client, auth_headers, second_auth_headers):
    # Alice does NOT follow Bob; Bob creates a post
    await create_post(client, second_auth_headers, {"caption": "Bob's post"})

    resp = await client.get("/posts/feed", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["posts"] == []


async def test_feed_no_auth(client):
    resp = await client.get("/posts/feed")
    assert resp.status_code == 401
