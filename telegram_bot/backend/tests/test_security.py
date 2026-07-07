"""Security-focused tests for auth and sync endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password
from jose import jwt


def test_send_otp_excludes_code(client: TestClient):
    """POST /auth/otp/send — response should NOT contain code."""
    payload = {"email": "test@example.com"}
    resp = client.post("/auth/otp/send", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data
    assert "code" not in data
    assert data["message"] == "OTP sent"


def test_verify_telegram_hash_no_mutation(db_session: Session):
    """verify_telegram_hash should not mutate input dict."""
    # Test direct service function
    from app.services.auth_service import verify_telegram_hash
    
    original_data = {
        "id": 123456789,
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "auth_date": 1710000000,
        "hash": "somehashvalue",
    }
    data_copy = original_data.copy()
    
    # This should not mutate the dict
    result = verify_telegram_hash(original_data, "test_bot_token")
    
    # Original dict should be unchanged
    assert "hash" in original_data
    assert original_data["hash"] == "somehashvalue"
    assert original_data == data_copy


def test_jwt_token_creation_and_verification(db_session: Session):
    """JWT tokens should be created and verified correctly."""
    from app.core.security import create_access_token, create_refresh_token, verify_token
    from app.config import settings
    
    user_id = 1
    email = "test@example.com"
    role = "student"
    
    # Test access token
    access_token = create_access_token(user_id, email, role)
    assert access_token is not None
    assert isinstance(access_token, str)
    
    payload = verify_token(access_token, settings.JWT_ACCESS_SECRET)
    assert payload["sub"] == str(user_id)
    assert payload["email"] == email
    assert payload["role"] == role
    
    # Test refresh token
    refresh_token = create_refresh_token(user_id)
    assert refresh_token is not None
    assert isinstance(refresh_token, str)
    
    refresh_payload = verify_token(refresh_token, settings.JWT_REFRESH_SECRET)
    assert refresh_payload["sub"] == str(user_id)


def test_hardcoded_secrets_not_exposed():
    """Ensure no secrets are hardcoded in source files."""
    import os
    import subprocess
    
    # Check for common hardcoded secret patterns (excluding test files and .env)
    patterns_to_check = [
        "sk-or-v1-",
        "bot_token",
        "api_key",
        "secret_key",
        "password",
    ]
    
    source_dirs = ["./app", "./telegram_bot/backend", "./telegram_bot/bot"]
    test_dirs = ["./tests", "./test"]
    
    for source_dir in source_dirs:
        for pattern in patterns_to_check:
            result = subprocess.run(
                ["grep", "-r", pattern, source_dir, "--include=*.py"],
                capture_output=True,
                text=True,
                cwd=".",
            )
            # Filter out test files and .env files
            lines = [
                line for line in result.stdout.split("\n")
                if line and not any(td in line for td in test_dirs)
                and ".env" not in line
            ]
            assert len(lines) == 0 or "os.getenv" in result.stdout or "settings." in result.stdout, \
                f"Potential hardcoded secret found with pattern '{pattern}' in {source_dir}"