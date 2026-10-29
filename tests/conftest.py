import pytest
import os 
from app import create_app
from app.db import get_db_connection
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("TASKHUB_DB_NAME", "taskhub_test")
    assert os.environ["TASKHUB_DB_NAME"] == "taskhub_test"
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()

@pytest.fixture
def test_task(client):
    response = client.post("/tasks", json={"title":"fixture task","status":"todo"})
    assert response.status_code == 201
    task = response.get_json()

    yield task
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id= %s",(task["id"],))