"""Pydantic schemas and domain model for the Todo API."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

TITLE_MAX_LENGTH = 200


class TodoCreate(BaseModel):
    """Payload for POST /todos."""

    title: str = Field(max_length=TITLE_MAX_LENGTH)
    priority: int = Field(default=1, ge=1, le=5)


class TodoUpdate(BaseModel):
    """Partial-update payload for PATCH /todos/{id}."""

    title: Optional[str] = Field(default=None, max_length=TITLE_MAX_LENGTH)
    done: Optional[bool] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)


class TodoOut(BaseModel):
    """Representation of a todo as returned by the API."""

    id: int
    title: str
    done: bool
    priority: int
    created_at: str


@dataclass
class Todo:
    """Domain object stored in the in-memory store."""

    id: int
    title: str
    priority: int
    done: bool = False
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_out(self) -> TodoOut:
        return TodoOut(
            id=self.id,
            title=self.title,
            done=self.done,
            priority=self.priority,
            created_at=self.created_at,
        )
