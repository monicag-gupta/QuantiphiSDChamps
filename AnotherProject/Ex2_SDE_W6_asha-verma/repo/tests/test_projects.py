from datetime import date

from tests.conftest import PROJECT1, USER1, USER2, USER3


def auth(user_id=USER1):
    return {"X-User-Id": user_id}


def test_list_projects(client):
    r = client.get("/v1/projects?page=1&page_size=10")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == PROJECT1


def test_list_projects_invalid_page(client):
    assert client.get("/v1/projects?page=0").status_code == 422


def test_create_project_requires_identity(client):
    r = client.post("/v1/projects", json={
        "name": "Migration Program", "start_date": "2026-09-01", "end_date": "2026-11-30"
    })
    assert r.status_code == 401


def test_create_project_and_manager_membership(client):
    r = client.post("/v1/projects", headers=auth(), json={
        "name": "Migration Program",
        "description": "Move legacy workloads",
        "start_date": "2026-09-01",
        "end_date": "2026-11-30",
        "status": "planned",
    })
    assert r.status_code == 201
    body = r.json()
    assert body["manager_id"] == USER1
    assert body["name"] == "Migration Program"


def test_create_project_rejects_bad_dates(client):
    r = client.post("/v1/projects", headers=auth(), json={
        "name": "Bad Dates", "start_date": "2026-11-01", "end_date": "2026-10-01"
    })
    assert r.status_code == 422


def test_get_project_404(client):
    assert client.get("/v1/projects/missing").status_code == 404


def test_manager_can_patch_project(client):
    r = client.patch(f"/v1/projects/{PROJECT1}", headers=auth(), json={"status": "on_hold"})
    assert r.status_code == 200
    assert r.json()["status"] == "on_hold"


def test_non_manager_cannot_patch_project(client):
    r = client.patch(f"/v1/projects/{PROJECT1}", headers=auth(USER2), json={"status": "on_hold"})
    assert r.status_code == 403


def test_empty_project_patch_is_422(client):
    assert client.patch(f"/v1/projects/{PROJECT1}", headers=auth(), json={}).status_code == 422


def test_add_member_duplicate_is_409(client):
    r = client.post(f"/v1/projects/{PROJECT1}/members", headers=auth(), json={"user_id": USER2, "role": "contributor"})
    assert r.status_code == 409


def test_add_inactive_member_is_404(client):
    r = client.post(f"/v1/projects/{PROJECT1}/members", headers=auth(), json={"user_id": USER3, "role": "viewer"})
    assert r.status_code == 404


def test_non_manager_cannot_add_member(client):
    r = client.post(f"/v1/projects/{PROJECT1}/members", headers=auth(USER2), json={"user_id": USER3, "role": "viewer"})
    assert r.status_code == 403


def test_summary(client):
    r = client.get(f"/v1/projects/{PROJECT1}/summary")
    assert r.status_code == 200
    body = r.json()
    assert body["total_tasks"] == 1
    assert body["completed_tasks"] == 0
    assert body["open_risks"] == 1
    assert body["total_logged_hours"] == 2.5


def test_manager_can_delete_project(client):
    r = client.delete(f"/v1/projects/{PROJECT1}", headers=auth())
    assert r.status_code == 204
    assert client.get(f"/v1/projects/{PROJECT1}").status_code == 404
