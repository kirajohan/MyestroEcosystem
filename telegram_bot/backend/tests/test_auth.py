def test_register_success(client):
    resp = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"


def test_register_duplicate(client):
    client.post("/auth/register", json={
        "email": "dup@example.com",
        "password": "password123",
        "full_name": "User",
    })
    resp = client.post("/auth/register", json={
        "email": "dup@example.com",
        "password": "password123",
        "full_name": "User",
    })
    assert resp.status_code == 409


def test_login_success(client):
    client.post("/auth/register", json={
        "email": "login@test.com",
        "password": "password123",
        "full_name": "Login User",
    })
    resp = client.post("/auth/login", json={
        "email": "login@test.com",
        "password": "password123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "email": "wrong@test.com",
        "password": "password123",
        "full_name": "Wrong User",
    })
    resp = client.post("/auth/login", json={
        "email": "wrong@test.com",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_jwt_refresh(client):
    reg = client.post("/auth/register", json={
        "email": "refresh@test.com",
        "password": "password123",
        "full_name": "Refresh User",
    })
    refresh_token = reg.json()["refresh_token"]

    resp = client.post("/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()