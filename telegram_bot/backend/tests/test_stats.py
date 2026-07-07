def test_get_stats(client, auth_headers):
    resp = client.get("/stats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_users" in data
    assert "active_users_7d" in data
    assert "today_messages" in data


def test_get_activity_chart(client, auth_headers):
    resp = client.get("/stats/activity?days=7", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)