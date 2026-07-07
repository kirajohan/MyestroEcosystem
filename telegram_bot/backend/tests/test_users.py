def test_list_users_admin(client, auth_headers):
    resp = client.get("/users", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_users_student_forbidden(client):
    # Register as student
    reg = client.post("/auth/register", json={
        "email": "student@test.com",
        "password": "password123",
        "full_name": "Student User",
        "role": "student",
    })
    token = reg.json()["access_token"]
    resp = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_get_user_profile(client, auth_headers):
    resp = client.get("/users/1", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "admin@test.com"


def test_delete_user(client, auth_headers):
    # Create a user to delete
    client.post("/auth/register", json={
        "email": "delete@test.com",
        "password": "password123",
        "full_name": "Delete User",
    })
    resp = client.delete("/users/2", headers=auth_headers)
    assert resp.status_code == 200