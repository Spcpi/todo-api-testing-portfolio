"""Integration tests for the Todo API (HTTP via FastAPI TestClient).

Each test docstring carries the test-case id from docs/test-cases.md.
"""
import pytest

from app.models import TITLE_MAX_LENGTH


class TestCreateTodo:
    def test_create_valid(self, client):
        """TC-001: 201 + echoed fields + ISO created_at."""
        r = client.post("/todos", json={"title": "buy milk", "priority": 2})
        assert r.status_code == 201
        body = r.json()
        assert body["title"] == "buy milk"
        assert body["priority"] == 2
        assert body["done"] is False
        assert body["id"] == 1
        assert "T" in body["created_at"]  # ISO-8601 shape

    def test_title_at_max_length(self, client):
        """TC-002: 200-char title accepted."""
        r = client.post("/todos", json={"title": "x" * 200})
        assert r.status_code == 201

    def test_title_too_long(self, client):
        """TC-003: 201-char title rejected with 422."""
        r = client.post("/todos", json={"title": "x" * 201})
        assert r.status_code == 422

    def test_missing_title(self, client):
        """TC-004: title required."""
        r = client.post("/todos", json={"priority": 3})
        assert r.status_code == 422

    @pytest.mark.parametrize("bad", [0, 6])
    def test_priority_out_of_range(self, client, bad):
        """TC-005: priority must be 1-5."""
        r = client.post("/todos", json={"title": "t", "priority": bad})
        assert r.status_code == 422

    def test_priority_defaults_to_one(self, client):
        """TC-006: omitted priority → 1."""
        r = client.post("/todos", json={"title": "t"})
        assert r.status_code == 201
        assert r.json()["priority"] == 1


class TestListTodos:
    def test_list_empty(self, client):
        """TC-010: empty store → empty items, total 0."""
        r = client.get("/todos")
        assert r.status_code == 200
        body = r.json()
        assert body["items"] == []
        assert body["total"] == 0
        assert body["has_next"] is False

    def test_list_contains_created(self, client):
        """TC-011: created todos appear in list."""
        client.post("/todos", json={"title": "a"})
        client.post("/todos", json={"title": "b"})
        body = client.get("/todos").json()
        assert body["total"] == 2
        assert [i["title"] for i in body["items"]] == ["a", "b"]

    def test_pagination_page1(self, client):
        """TC-012 (API layer): page 1 limit 5 → ids 1-5, has_next."""
        for i in range(7):
            client.post("/todos", json={"title": f"t{i}"})
        r = client.get("/todos", params={"limit": 5})
        assert r.status_code == 200
        body = r.json()
        assert [i["id"] for i in body["items"]] == [1, 2, 3, 4, 5]
        assert body["has_next"] is True

    def test_pagination_page2(self, client):
        """TC-013 (API layer): page 2 limit 5 → ids 6-7."""
        for i in range(7):
            client.post("/todos", json={"title": f"t{i}"})
        r = client.get("/todos", params={"limit": 5, "page": 2})
        assert r.status_code == 200
        body = r.json()
        assert [i["id"] for i in body["items"]] == [6, 7]
        assert body["has_next"] is False

    @pytest.mark.parametrize("params", [{"page": 0}, {"limit": 0}, {"limit": 101}])
    def test_pagination_invalid_params(self, client, params):
        """TC-014/TC-015: page/limit bounds enforced."""
        for i in range(3):
            client.post("/todos", json={"title": f"t{i}"})
        r = client.get("/todos", params=params)
        assert r.status_code == 422


class TestGetTodo:
    def test_get_existing(self, client):
        """TC-020: 200 with full body."""
        client.post("/todos", json={"title": "a"})
        r = client.get("/todos/1")
        assert r.status_code == 200
        assert r.json()["title"] == "a"

    def test_get_unknown_404(self, client):
        """TC-021: unknown id → 404 with detail."""
        r = client.get("/todos/999")
        assert r.status_code == 404
        assert r.json()["detail"] == "todo not found"

    def test_get_non_numeric_422(self, client):
        """TC-022: non-numeric path param → 422."""
        r = client.get("/todos/abc")
        assert r.status_code == 422


class TestPatchTodo:
    def test_mark_done(self, client):
        """TC-030: done flips to true."""
        client.post("/todos", json={"title": "a"})
        r = client.patch("/todos/1", json={"done": True})
        assert r.status_code == 200
        assert r.json()["done"] is True

    def test_rename(self, client):
        """TC-031: title updated."""
        client.post("/todos", json={"title": "old"})
        r = client.patch("/todos/1", json={"title": "new"})
        assert r.status_code == 200
        assert r.json()["title"] == "new"

    def test_partial_update_keeps_other_fields(self, client):
        """TC-032: patching done leaves priority alone."""
        client.post("/todos", json={"title": "a", "priority": 3})
        r = client.patch("/todos/1", json={"done": True})
        body = r.json()
        assert body["done"] is True
        assert body["priority"] == 3
        assert body["title"] == "a"

    def test_patch_unknown_404(self, client):
        """TC-033: unknown id → 404."""
        r = client.patch("/todos/999", json={"done": True})
        assert r.status_code == 404

    def test_patch_invalid_priority(self, client):
        """TC-034: priority 6 rejected."""
        client.post("/todos", json={"title": "a"})
        r = client.patch("/todos/1", json={"priority": 6})
        assert r.status_code == 422


class TestDeleteTodo:
    def test_delete_existing(self, client):
        """TC-040: delete → 200; resource gone afterwards."""
        client.post("/todos", json={"title": "a"})
        r = client.delete("/todos/1")
        assert r.status_code == 200
        assert r.json()["deleted"] is True
        assert client.get("/todos/1").status_code == 404

    def test_delete_unknown_404(self, client):
        """TC-041: unknown id → 404 (BUG-001: currently 200)."""
        r = client.delete("/todos/999")
        assert r.status_code == 404

    def test_delete_twice(self, client):
        """TC-042: second delete → 404."""
        client.post("/todos", json={"title": "a"})
        client.delete("/todos/1")
        r = client.delete("/todos/1")
        assert r.status_code == 404


class TestStats:
    def test_stats_mixed(self, client):
        """TC-050: 1/3 done → 33.3."""
        for title in ("a", "b", "c"):
            client.post("/todos", json={"title": title})
        client.patch("/todos/1", json={"done": True})
        body = client.get("/todos/stats").json()
        assert body["total"] == 3
        assert body["done"] == 1
        assert body["pending"] == 2
        assert body["completion_rate"] == 33.3

    def test_stats_empty(self, client):
        """TC-051: empty store → 200 with zeros (BUG-004: currently 500)."""
        r = client.get("/todos/stats")
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 0
        assert body["completion_rate"] == 0.0

    def test_stats_all_done(self, client):
        """TC-052: all done → 100.0."""
        for i in range(4):
            client.post("/todos", json={"title": f"t{i}"})
        for i in range(1, 5):
            client.patch(f"/todos/{i}", json={"done": True})
        assert client.get("/todos/stats").json()["completion_rate"] == 100.0
