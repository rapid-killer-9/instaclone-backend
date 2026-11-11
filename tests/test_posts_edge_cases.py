"""
Post edge cases: field validation boundaries, pagination, and like/comment consistency.
"""
import pytest

from tests.conftest import USER_A, USER_B, VALID_POST


# ── caption boundaries ────────────────────────────────────────────────────────

async def test_caption_at_max_length_accepted(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "caption": "x" * 100}, headers=auth_headers)
    assert resp.status_code == 201


async def test_caption_over_max_length_rejected(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "caption": "x" * 101}, headers=auth_headers)
    assert resp.status_code == 400


async def test_caption_whitespace_only_rejected(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "caption": "   "}, headers=auth_headers)
    assert resp.status_code == 400


async def test_caption_empty_rejected(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "caption": ""}, headers=auth_headers)
    assert resp.status_code == 400


# ── description boundaries ────────────────────────────────────────────────────

async def test_description_at_max_length_accepted(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "description": "d" * 500}, headers=auth_headers)
    assert resp.status_code == 201


async def test_description_over_max_length_rejected(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "description": "d" * 501}, headers=auth_headers)
    assert resp.status_code == 400


async def test_description_empty_string_accepted(client, auth_headers):
    """Empty description bypasses validation and is stored as-is."""
    resp = await client.post("/posts/", json={**VALID_POST, "description": ""}, headers=auth_headers)
    assert resp.status_code == 201


# ── hashtag boundaries ────────────────────────────────────────────────────────

async def test_exactly_10_hashtags_accepted(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "hashtags": ["tag"] * 10}, headers=auth_headers)
    assert resp.status_code == 201


async def test_11_hashtags_rejected(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "hashtags": ["tag"] * 11}, headers=auth_headers)
    assert resp.status_code == 400


async def test_hashtag_at_max_length_accepted(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "hashtags": ["h" * 20]}, headers=auth_headers)
    assert resp.status_code == 201


async def test_hashtag_over_max_length_rejected(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "hashtags": ["h" * 21]}, headers=auth_headers)
    assert resp.status_code == 400


async def test_empty_hashtag_list_accepted(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "hashtags": []}, headers=auth_headers)
    assert resp.status_code == 201


# ── media / music url validation ──────────────────────────────────────────────

async def test_media_url_ftp_scheme_rejected(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "media_url": "ftp://example.com/img.jpg"}, headers=auth_headers)
    assert resp.status_code == 400


async def test_media_url_relative_path_rejected(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "media_url": "/images/photo.jpg"}, headers=auth_headers)
    assert resp.status_code == 400


async def test_music_url_valid_accepted(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "music_url": "https://example.com/song.mp3"}, headers=auth_headers)
    assert resp.status_code == 201


async def test_music_url_invalid_scheme_rejected(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "music_url": "ftp://example.com/song.mp3"}, headers=auth_headers)
    assert resp.status_code == 400


async def test_music_url_relative_path_rejected(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "music_url": "/songs/track.mp3"}, headers=auth_headers)
    assert resp.status_code == 400


# ── category validation ───────────────────────────────────────────────────────

async def test_all_valid_categories_accepted(client, auth_headers):
    for category in ["Tech", "Entertainment", "Business", "Sports", "Music", "Art", "Education"]:
        resp = await client.post("/posts/", json={**VALID_POST, "caption": f"{category} post", "category": category}, headers=auth_headers)
        assert resp.status_code == 201, f"Category {category!r} was unexpectedly rejected"


async def test_case_sensitive_category_rejected(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "category": "tech"}, headers=auth_headers)
    assert resp.status_code == 422


# ── tagged users ──────────────────────────────────────────────────────────────

async def test_tag_existing_user_accepted(client, auth_headers, second_auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "tagged_users": [USER_B["username"]]}, headers=auth_headers)
    assert resp.status_code == 201


async def test_tag_nonexistent_user_rejected(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "tagged_users": ["nobody_here"]}, headers=auth_headers)
    assert resp.status_code == 400


async def test_empty_tagged_users_list_accepted(client, auth_headers):
    resp = await client.post("/posts/", json={**VALID_POST, "tagged_users": []}, headers=auth_headers)
    assert resp.status_code == 201


# ── pagination validation ─────────────────────────────────────────────────────

async def test_pagination_page_zero_rejected(client):
    resp = await client.get("/posts/", params={"page": 0})
    assert resp.status_code == 422


async def test_pagination_negative_page_rejected(client):
    resp = await client.get("/posts/", params={"page": -1})
    assert resp.status_code == 422


async def test_pagination_limit_zero_rejected(client):
    resp = await client.get("/posts/", params={"limit": 0})
    assert resp.status_code == 422


async def test_pagination_limit_at_max_accepted(client):
    resp = await client.get("/posts/", params={"limit": 100})
    assert resp.status_code == 200


async def test_pagination_limit_over_max_rejected(client):
    resp = await client.get("/posts/", params={"limit": 101})
    assert resp.status_code == 422


async def test_pagination_beyond_total_returns_empty(client, auth_headers):
    for i in range(3):
        await client.post("/posts/", json={**VALID_POST, "caption": f"Post {i}"}, headers=auth_headers)

    resp = await client.get("/posts/", params={"page": 999, "limit": 20})
    assert resp.status_code == 200
    assert resp.json()["posts"] == []


async def test_pagination_correct_page_slicing(client, auth_headers):
    captions = [f"Post {i}" for i in range(5)]
    for cap in captions:
        await client.post("/posts/", json={**VALID_POST, "caption": cap}, headers=auth_headers)

    page1 = (await client.get("/posts/", params={"page": 1, "limit": 2})).json()["posts"]
    page2 = (await client.get("/posts/", params={"page": 2, "limit": 2})).json()["posts"]
    page3 = (await client.get("/posts/", params={"page": 3, "limit": 2})).json()["posts"]

    assert len(page1) == 2
    assert len(page2) == 2
    assert len(page3) == 1
    # No post appears on two pages
    ids_p1 = {p["_id"] for p in page1}
    ids_p2 = {p["_id"] for p in page2}
    ids_p3 = {p["_id"] for p in page3}
    assert not (ids_p1 & ids_p2)
    assert not (ids_p2 & ids_p3)


# ── comment boundaries ────────────────────────────────────────────────────────

async def _make_post(client, headers):
    resp = await client.post("/posts/", json=VALID_POST, headers=headers)
    assert resp.status_code == 201
    return resp.json()["post"]["_id"]


async def test_comment_at_max_length_accepted(client, auth_headers):
    post_id = await _make_post(client, auth_headers)
    resp = await client.post(f"/posts/{post_id}/comments", json={"text": "c" * 500}, headers=auth_headers)
    assert resp.status_code == 201


async def test_comment_over_max_length_rejected(client, auth_headers):
    post_id = await _make_post(client, auth_headers)
    resp = await client.post(f"/posts/{post_id}/comments", json={"text": "c" * 501}, headers=auth_headers)
    assert resp.status_code == 422


async def test_comment_single_char_accepted(client, auth_headers):
    post_id = await _make_post(client, auth_headers)
    resp = await client.post(f"/posts/{post_id}/comments", json={"text": "!"}, headers=auth_headers)
    assert resp.status_code == 201


async def test_comment_missing_text_field(client, auth_headers):
    post_id = await _make_post(client, auth_headers)
    resp = await client.post(f"/posts/{post_id}/comments", json={}, headers=auth_headers)
    assert resp.status_code == 422


# ── like / unlike consistency ─────────────────────────────────────────────────

async def test_multiple_users_like_same_post(client, auth_headers, second_auth_headers):
    post_id = await _make_post(client, auth_headers)
    r1 = await client.post(f"/posts/{post_id}/like", headers=auth_headers)
    r2 = await client.post(f"/posts/{post_id}/like", headers=second_auth_headers)
    assert r1.status_code == 200
    assert r2.status_code == 200


async def test_like_unlike_like_cycle(client, auth_headers):
    post_id = await _make_post(client, auth_headers)
    await client.post(f"/posts/{post_id}/like", headers=auth_headers)
    await client.delete(f"/posts/{post_id}/like", headers=auth_headers)
    resp = await client.post(f"/posts/{post_id}/like", headers=auth_headers)
    assert resp.status_code == 200


async def test_unlike_invalid_post_id(client, auth_headers):
    resp = await client.delete("/posts/invalid-id/like", headers=auth_headers)
    assert resp.status_code == 400


async def test_like_invalid_post_id(client, auth_headers):
    resp = await client.post("/posts/invalid-id/like", headers=auth_headers)
    assert resp.status_code == 400


# ── feed pagination ───────────────────────────────────────────────────────────

async def test_feed_pagination_returns_correct_slice(client, auth_headers, second_auth_headers):
    await client.post(f"/users/follow/{USER_B['username']}", headers=auth_headers)
    for i in range(5):
        await client.post("/posts/", json={**VALID_POST, "caption": f"Bob {i}"}, headers=second_auth_headers)

    page1 = (await client.get("/posts/feed", headers=auth_headers, params={"page": 1, "limit": 2})).json()
    page2 = (await client.get("/posts/feed", headers=auth_headers, params={"page": 2, "limit": 2})).json()

    assert len(page1["posts"]) == 2
    assert len(page2["posts"]) == 2
    ids_p1 = {p["_id"] for p in page1["posts"]}
    ids_p2 = {p["_id"] for p in page2["posts"]}
    assert not (ids_p1 & ids_p2)


async def test_feed_beyond_total_returns_empty(client, auth_headers, second_auth_headers):
    await client.post(f"/users/follow/{USER_B['username']}", headers=auth_headers)
    await client.post("/posts/", json={**VALID_POST, "caption": "Only one"}, headers=second_auth_headers)

    resp = await client.get("/posts/feed", headers=auth_headers, params={"page": 999, "limit": 20})
    assert resp.status_code == 200
    assert resp.json()["posts"] == []
