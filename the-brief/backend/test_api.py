"""Tests for API endpoints."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _set_db_path(tmp_path):
    """Use a temp database for each test."""
    os.environ["DB_PATH"] = str(tmp_path / "test.db")
    # Re-import to pick up the new DB_PATH
    import importlib

    import app as app_module
    import database as db_module

    importlib.reload(db_module)
    importlib.reload(app_module)
    yield


@pytest.fixture
def client():
    from app import app

    return TestClient(app)


class TestHealth:
    def test_health(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestChapters:
    def test_list_chapters(self, client):
        resp = client.get("/api/chapters")
        assert resp.status_code == 200
        chapters = resp.json()
        assert len(chapters) >= 1
        assert chapters[0]["id"] == "chapter-01"

    def test_list_characters(self, client):
        resp = client.get("/api/characters")
        assert resp.status_code == 200
        chars = resp.json()
        assert "margaret" in chars


class TestGameFlow:
    def test_new_game(self, client):
        resp = client.post("/api/game/new")
        assert resp.status_code == 200
        data = resp.json()
        assert "save_id" in data
        assert data["scene"]["id"] == "late_night_office"

    def test_load_game(self, client):
        new = client.post("/api/game/new").json()
        resp = client.get(f"/api/game/{new['save_id']}")
        assert resp.status_code == 200
        assert resp.json()["current_scene"] == "late_night_office"

    def test_load_nonexistent(self, client):
        resp = client.get("/api/game/nonexistent")
        assert resp.status_code == 404

    def test_get_scene(self, client):
        new = client.post("/api/game/new").json()
        resp = client.get(f"/api/game/{new['save_id']}/scene")
        assert resp.status_code == 200
        scene = resp.json()
        assert scene["id"] == "late_night_office"
        assert len(scene["choices"]) == 2

    def test_make_choice(self, client):
        new = client.post("/api/game/new").json()
        resp = client.post(
            f"/api/game/{new['save_id']}/choose",
            json={"choice_index": 0},
        )
        assert resp.status_code == 200
        scene = resp.json()
        assert scene["id"] == "margaret_details"

    def test_invalid_choice_index(self, client):
        new = client.post("/api/game/new").json()
        resp = client.post(
            f"/api/game/{new['save_id']}/choose",
            json={"choice_index": 99},
        )
        assert resp.status_code == 400

    def test_research_empty_at_start(self, client):
        new = client.post("/api/game/new").json()
        resp = client.get(f"/api/game/{new['save_id']}/research")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_research_after_choice(self, client):
        new = client.post("/api/game/new").json()
        save_id = new["save_id"]
        # Skip to research_start
        client.post(f"/api/game/{save_id}/choose", json={"choice_index": 1})
        # Choose UCC research (adds ucc_section_2)
        client.post(f"/api/game/{save_id}/choose", json={"choice_index": 0})
        resp = client.get(f"/api/game/{save_id}/research")
        items = resp.json()
        assert len(items) == 1
        assert items[0]["id"] == "ucc_section_2"


class TestSaveManagement:
    def test_list_saves(self, client):
        client.post("/api/game/new")
        client.post("/api/game/new")
        resp = client.get("/api/saves")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_delete_save(self, client):
        new = client.post("/api/game/new").json()
        resp = client.delete(f"/api/game/{new['save_id']}")
        assert resp.status_code == 200
        resp = client.get(f"/api/game/{new['save_id']}")
        assert resp.status_code == 404

    def test_delete_nonexistent(self, client):
        resp = client.delete("/api/game/nonexistent")
        assert resp.status_code == 404
