
from app.db import get_db_connection
import pytest


@pytest.mark.parametrize(
    "payload",
    [
        {"title": ""},
        {"title": "   "},
        {"title": 123},
        {"title": None},
        {"title": "a" * 201},
        {"status": "unknown"},
        {},
        {"title": "Changed title", "status": "unknown"},
    ]
)
def test_patch_task_invalid_input(client, test_task, payload):
    task_id = test_task["id"]
    response = client.patch(f"/tasks/{task_id}", json = payload)
    assert response.status_code == 400

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.get_json()["title"] == test_task["title"]
    assert get_response.get_json()["status"] == test_task["status"]

@pytest.mark.parametrize(
    "payload",
    [
        {"title": "", "status": "todo"},
        {"title": "   ", "status": "todo"},
        {"title": 123, "status": "todo"},
        {"title": None, "status": "todo"},
        {"title": "a" * 201, "status": "todo"},
        {"title": "Valid title", "status": "unknown"},
    ]
)
def test_update_task_invalid_input(client, test_task, payload):
    task_id = test_task["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json=payload
    )
    assert response.status_code == 400
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.get_json()["title"] == test_task["title"]
    assert get_response.get_json()["status"] == test_task["status"]


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "", "status": "todo"},
        {"title": "   ", "status": "todo"},
        {"title": "Test task", "status": "unknown"},
        {"title":"","status":"completed"},
        {"title": 123, "status": "todo"},
        {"title": 123, "status": "todo"},
        {"title": None, "status": "todo"},
        {"title": "a" * 201, "status": "todo"},
    ]
)
def test_create_task_invalid_input(client, payload):
    response = client.post("/tasks", json=payload)

    assert response.status_code == 400
    
@pytest.mark.parametrize("length",[199,200])
def test_create_task_valid_title_length(client,length):
    title = "a"*length
    response = client.post("/tasks",json={"title":title,"status":"todo"})
    assert response.status_code == 201
    task = response.get_json()
    task_id = task["id"]
    try:
        assert len(task["title"]) == length
        assert task["title"] == title
    finally:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    


def test_uses_test_database(client):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database()")
            result = cur.fetchone()
    assert result["current_database"] == "taskhub_test"

def test_get_tasks(client):
    response = client.get("/tasks")
    assert response.status_code == 200

def test_get_nonexit_task(client):
    response = client.get("/tasks/7")
    assert response.status_code == 404

def test_post_invalid_title(client):
    response = client.post("/tasks",
                           json={"title":"","status":"todo"})
    assert response.status_code == 400

def test_post_invalid_status(client):
    response = client.post("/tasks", json={"title":"study", "status":"finished"})
    assert response.status_code == 400

def test_create_task(client):
  
    response = client.post("/tasks", json={"title":"wash clothes","status":"todo"})
    assert response.status_code == 201
    task = response.get_json()
    task_id = task["id"]


    try: 
        assert task["title"] == "wash clothes"
        assert task["status"] == "todo"

    finally:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tasks WHERE id = %s",(task_id,))

def test_update_task(client):
    create_response = client.post("/tasks",json={"title":"original_task","status":"todo"})
    assert create_response.status_code == 201
    updated_task = create_response.get_json()
    task_id = updated_task["id"]

    try:
        response = client.put(f"/tasks/{task_id}",json={"title":"updated_task", "status":"done"})
        assert response.status_code == 200
        updated_task = response.get_json()
        assert updated_task["title"] == "updated_task"
        assert updated_task["status"] == "done"

        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 200
        assert get_response.get_json()["status"] == "done"

    finally:
        with get_db_connection() as conn:
            with conn.cursor()as cur:
                cur.execute("DELETE FROM tasks WHERE id = %s",(task_id,))




def test_delete_task(client,test_task):
    
    task_id = test_task["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    assert response.data == b""
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404

def test_patch_task_title_only(client,test_task):
    task_id = test_task["id"]
    response = client.patch(f"/tasks/{task_id}",json={"title":"updated by patch"})
    assert response.status_code == 200
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.get_json()["title"] == "updated by patch"
    assert get_response.get_json()["status"]== test_task["status"]

def test_patch_task_status_only(client,test_task):
    task_id = test_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status":"in_progress"})
    assert response.status_code ==200
    get_response = client.get(f"/tasks/{task_id}")

    assert get_response.status_code == 200
    assert get_response.get_json()["status"] == "in_progress"
    assert get_response.get_json()["title"] == test_task["title"]

def test_patch_task_both_fields(client, test_task):
    task_id = test_task["id"]
    response = client.patch(f"/tasks/{task_id}", json = {"title":"updated_both", "status":"done"})
    assert response.status_code == 200
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.get_json()["title"] == "updated_both"
    assert get_response.get_json()["status"] == "done"




           
       
