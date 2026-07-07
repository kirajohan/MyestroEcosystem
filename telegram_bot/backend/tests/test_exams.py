def test_list_exams(client, auth_headers):
    resp = client.get("/exams", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_create_exam_admin(client, auth_headers):
    resp = client.post("/exams", json={
        "title": "Test Exam",
        "cefr_level": "B1",
        "total_duration": 60,
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Test Exam"


def test_get_exam_detail(client, auth_headers):
    create = client.post("/exams", json={
        "title": "Detail Exam",
        "cefr_level": "A2",
        "total_duration": 30,
    }, headers=auth_headers)
    exam_id = create.json()["id"]

    resp = client.get(f"/exams/{exam_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Detail Exam"


def test_delete_exam(client, auth_headers):
    create = client.post("/exams", json={
        "title": "Delete Exam",
        "cefr_level": "C1",
        "total_duration": 90,
    }, headers=auth_headers)
    exam_id = create.json()["id"]

    resp = client.delete(f"/exams/{exam_id}", headers=auth_headers)
    assert resp.status_code == 200