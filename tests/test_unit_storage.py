"""Unit tests for TodoStore (no HTTP) — pagination & stats math.

Each test docstring carries the test-case id from docs/test-cases.md.
"""
import pytest

from app.storage import TodoStore


@pytest.fixture
def store_with_todos():
    store = TodoStore()
    for i in range(7):
        store.add(title=f"task {i + 1}", priority=(i % 5) + 1)
    return store


class TestStorePagination:
    def test_page1_returns_first_five(self, store_with_todos):
        """TC-012: page 1 / limit 5 contains items 1-5."""
        result = store_with_todos.list(page=1, limit=5)
        ids = [t.id for t in result["items"]]
        assert ids == [1, 2, 3, 4, 5]
        assert result["has_next"] is True

    def test_page2_returns_next_two(self, store_with_todos):
        """TC-013: page 2 / limit 5 contains items 6-7 only."""
        result = store_with_todos.list(page=2, limit=5)
        ids = [t.id for t in result["items"]]
        assert ids == [6, 7]
        assert result["has_next"] is False

    def test_total_counts_every_todo(self, store_with_todos):
        """TC-011 (unit layer): total reflects all stored items."""
        result = store_with_todos.list(page=1, limit=3)
        assert result["total"] == 7


class TestStoreStats:
    def test_completion_rate_is_precise(self):
        """TC-050: 1 done of 3 → 33.3 (float, one decimal)."""
        store = TodoStore()
        store.add("a")
        store.add("b")
        store.add("c")
        store.update(1, {"done": True})
        stats = store.stats()
        assert stats["total"] == 3
        assert stats["done"] == 1
        assert stats["pending"] == 2
        assert stats["completion_rate"] == 33.3

    def test_stats_on_empty_store(self):
        """TC-051: empty store → zeros, not an exception."""
        store = TodoStore()
        stats = store.stats()
        assert stats["total"] == 0
        assert stats["done"] == 0
        assert stats["pending"] == 0
        assert stats["completion_rate"] == 0.0

    def test_stats_all_done(self):
        """TC-052: all done → 100.0."""
        store = TodoStore()
        for i in range(4):
            store.add(f"t{i}")
        for i in range(1, 5):
            store.update(i, {"done": True})
        assert store.stats()["completion_rate"] == 100.0
