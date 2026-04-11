from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from secure_app.api import create_app


def test_api_add_and_list_notes(tmp_path: Path) -> None:
    app = create_app(data_dir=tmp_path)
    client = TestClient(app)

    r = client.get("/notes")
    assert r.status_code == 200
    assert r.json() == []

    r = client.post("/notes", json={"text": "hello"})
    assert r.status_code == 200
    note = r.json()
    assert note["text"] == "hello"
    assert "id" in note

    r = client.get("/notes")
    assert r.status_code == 200
    notes = r.json()
    assert len(notes) == 1
    assert notes[0]["id"] == note["id"]


def test_api_demo_shape() -> None:
    app = create_app(data_dir=Path("data"))
    client = TestClient(app)

    r = client.get("/demo")
    assert r.status_code == 200
    body = r.json()
    assert body["email_masked"].endswith("@example.com")
    assert body["password_hash"].startswith("pbkdf2_sha256$")
