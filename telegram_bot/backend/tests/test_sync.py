"""Sync API endpoint integration tests."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password


def test_sync_user_get_existing(client: TestClient, db_session: Session):
    """GET /sync/user/{telegram_id} — existing user returns 200."""
    user = User(
        email="sync@test.com",
        password_hash=hash_password("password123"),
        full_name="Sync User",
        telegram_id=123456789,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    resp = client.get("/sync/user/123456789")
    assert resp.status_code == 200
    data = resp.json()
    assert data["telegram_id"] == 123456789
    assert data["full_name"] == "Sync User"


def test_sync_user_get_not_found(client: TestClient):
    """GET /sync/user/{telegram_id} — non-existing user returns 404."""
    resp = client.get("/sync/user/999999999")
    assert resp.status_code == 404


def test_sync_user_post_create(client: TestClient, db_session: Session):
    """POST /sync/user — create new user."""
    payload = {
        "telegram_id": 111222333,
        "telegram_username": "testuser",
        "phone": "+998901234567",
        "full_name": "Test User",
        "cefr_level": "B1",
        "lang": "uz",
        "auth_provider": "telegram",
    }
    resp = client.post("/sync/user", json=payload)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["telegram_id"] == 111222333
    assert data["full_name"] == "Test User"


def test_sync_user_post_duplicate(client: TestClient, db_session: Session):
    """POST /sync/user — duplicate telegram_id returns 409."""
    user = User(
        email="dup@test.com",
        password_hash=hash_password("password123"),
        full_name="Duplicate User",
        telegram_id=444555666,
    )
    db_session.add(user)
    db_session.commit()

    payload = {
        "telegram_id": 444555666,
        "full_name": "Another Name",
        "phone": "+998901234567",
        "auth_provider": "telegram",
    }
    resp = client.post("/sync/user", json=payload)
    assert resp.status_code == 409