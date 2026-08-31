"""Shared fixtures: a fresh store + client per test (isolation)."""
import pytest
from fastapi.testclient import TestClient

from app.main import app, get_store
from app.storage import TodoStore


@pytest.fixture
def store() -> TodoStore:
    return TodoStore()


@pytest.fixture
def client(store):
    """TestClient wired to a fresh per-test store via dependency override."""
    app.dependency_overrides[get_store] = lambda: store
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
