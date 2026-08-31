"""Todo API — a small FastAPI service used as a software-testing portfolio target."""
from fastapi import Depends, FastAPI, HTTPException, Query, Request

from app.models import TodoCreate, TodoUpdate, TodoOut
from app.storage import TodoStore

app = FastAPI(
    title="Todo API",
    version="1.0.0",
    description="A small task-management REST API (demo target for testing).",
)

# Default store for a live server; tests replace it via `app.state.store`.
app.state.store = TodoStore()


def get_store(request: Request) -> TodoStore:
    return request.app.state.store


@app.get("/todos/stats")
def stats(store: TodoStore = Depends(get_store)) -> dict:
    return store.stats()


@app.post("/todos", status_code=201)
def create_todo(payload: TodoCreate, store: TodoStore = Depends(get_store)) -> TodoOut:
    todo = store.add(payload.title, payload.priority)
    return todo.to_out()


@app.get("/todos")
def list_todos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    store: TodoStore = Depends(get_store),
) -> dict:
    result = store.list(page=page, limit=limit)
    return {
        "items": [t.to_out() for t in result["items"]],
        "page": result["page"],
        "limit": result["limit"],
        "total": result["total"],
        "has_next": result["has_next"],
    }


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int, store: TodoStore = Depends(get_store)) -> TodoOut:
    todo = store.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
    return todo.to_out()


@app.patch("/todos/{todo_id}")
def update_todo(
    todo_id: int, payload: TodoUpdate, store: TodoStore = Depends(get_store)
) -> TodoOut:
    todo = store.update(todo_id, payload.model_dump(exclude_unset=True))
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
    return todo.to_out()


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, store: TodoStore = Depends(get_store)) -> dict:
    deleted = store.remove(todo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="todo not found")
    return {"deleted": True}
