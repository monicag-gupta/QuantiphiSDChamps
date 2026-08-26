from tests.conftest import PROJECT1, TASK1, USER1, USER2, USER4


def auth(user_id=USER1):
    return {"X-User-Id": user_id}


def test_list_project_tasks(client):
    r = client.get(f"/v1/projects/{PROJECT1}/tasks")
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_member_can_create_task(client):
    r = client.post(f"/v1/projects/{PROJECT1}/tasks", headers=auth(USER2), json={
        "title": "Build endpoint", "assignee_id": USER2, "priority": "high",
        "due_date": "2026-10-01", "estimate_hours": 8
    })
    assert r.status_code == 201
    assert r.json()["assignee_id"] == USER2


def test_create_task_rejects_nonmember_assignee(client):
    r = client.post(f"/v1/projects/{PROJECT1}/tasks", headers=auth(), json={
        "title": "External task", "assignee_id": "99999999-9999-9999-9999-999999999999"
    })
    assert r.status_code == 422


def test_create_task_rejects_due_date_outside_project(client):
    r = client.post(f"/v1/projects/{PROJECT1}/tasks", headers=auth(), json={
        "title": "Late task", "due_date": "2027-01-01"
    })
    assert r.status_code == 422


def test_missing_task_404(client):
    assert client.get("/v1/tasks/missing").status_code == 404


def test_assignee_can_transition_task(client):
    r = client.patch(f"/v1/tasks/{TASK1}", headers=auth(USER2), json={"status": "in_progress"})
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"


def test_illegal_transition_returns_409(client):
    r = client.patch(f"/v1/tasks/{TASK1}", headers=auth(USER2), json={"status": "done"})
    assert r.status_code == 409


def test_unrelated_user_cannot_patch_task(client):
    r = client.patch(f"/v1/tasks/{TASK1}", headers=auth(USER4), json={"status": "in_progress"})
    assert r.status_code == 403


def test_empty_task_patch_422(client):
    assert client.patch(f"/v1/tasks/{TASK1}", headers=auth(USER2), json={}).status_code == 422


def test_manager_can_delete_task(client):
    r = client.delete(f"/v1/tasks/{TASK1}", headers=auth())
    assert r.status_code == 204
    assert client.get(f"/v1/tasks/{TASK1}").status_code == 404


def test_assignee_cannot_delete_task(client):
    r = client.delete(f"/v1/tasks/{TASK1}", headers=auth(USER2))
    assert r.status_code == 403
