"""In-memory todo store — the single source of truth for the API."""
from itertools import count
from typing import List, Optional

from app.models import Todo


class TodoStore:
    """Simple thread-unsafe in-memory store (fine for a demo service)."""

    def __init__(self) -> None:
        self._items: List[Todo] = []
        self._next_id = count(1)

    # -- CRUD -----------------------------------------------------------

    def add(self, title: str, priority: int = 1) -> Todo:
        todo = Todo(id=next(self._next_id), title=title, priority=priority)
        self._items.append(todo)
        return todo

    def get(self, todo_id: int) -> Optional[Todo]:
        return next((t for t in self._items if t.id == todo_id), None)

    def update(self, todo_id: int, fields: dict) -> Optional[Todo]:
        todo = self.get(todo_id)
        if todo is None:
            return None
        for key, value in fields.items():
            setattr(todo, key, value)
        return todo

    def remove(self, todo_id: int) -> bool:
        todo = self.get(todo_id)
        if todo is None:
            return False
        self._items.remove(todo)
        return True

    # -- Querying -------------------------------------------------------

    def list(self, page: int = 1, limit: int = 10) -> dict:
        """Return one page of todos plus paging metadata.

        Contract: `page` is 1-based. Page 1 with limit 5 must contain the
        first five todos; `total` always counts every stored todo.
        """
        total = len(self._items)
        start = (page - 1) * limit
        items = self._items[start : start + limit]
        return {
            "items": items,
            "page": page,
            "limit": limit,
            "total": total,
            "has_next": start + limit < total,
        }

    def stats(self) -> dict:
        """Return aggregate statistics for the stored todos.

        Contract: `completion_rate` is a float 0.0–100.0 (1 decimal place).
        An empty store must yield zeros, not an error.
        """
        total = len(self._items)
        if total == 0:
            return {"total": 0, "done": 0, "pending": 0, "completion_rate": 0.0}
        done = sum(1 for t in self._items if t.done)
        rate = round(done / total * 100, 1)
        return {
            "total": total,
            "done": done,
            "pending": total - done,
            "completion_rate": rate,
        }
