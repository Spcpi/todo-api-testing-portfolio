# Bug Reports — Todo API v1.0.0

All bugs below were **found by the automated test suite** (run log:
`test-run-buggy.log`), documented here, then fixed and verified with
regression tests. First failing run: `11 failed, 23 passed`.

---

## BUG-001 — DELETE on a non-existent id returns 200 instead of 404

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Priority** | P1 |
| **Endpoint** | `DELETE /todos/{todo_id}` |
| **Found by** | TC-041 (`test_delete_unknown_404`), TC-042 (`test_delete_twice`) |
| **Status** | Fixed |

**Steps to reproduce**

1. `DELETE /todos/999` against a store that has no todo 999.

**Expected:** `404 Not Found`
**Actual:** `200 OK` with body `{"deleted": false}`

**Root cause:** `delete_todo` in `app/main.py` returns a normal response for
the not-found branch instead of raising `HTTPException(404)`. A client cannot
distinguish "deleted" from "nothing was there" by status code alone, which
breaks REST semantics and idempotency-check flows.

**Fix:** raise `HTTPException(status_code=404, detail="todo not found")`.

---

## BUG-002 — Pagination skips items (off-by-one on page offset)

| Field | Value |
|---|---|
| **Severity** | High |
| **Priority** | P1 |
| **Endpoint** | `GET /todos?page=&limit=` |
| **Found by** | TC-011/012/013 (unit + API pagination tests) |
| **Status** | Fixed |

**Steps to reproduce**

1. Create 7 todos.
2. `GET /todos?limit=5` (page defaults to 1).

**Expected:** items 1–5, `has_next: true`
**Actual:** empty list — page 1 already skips 5 rows; page 2 returns items
6–7 instead of being the second page. Worse: with the default limit 10 and
only 2 todos, `GET /todos` returns **no items at all**.

**Root cause:** `TodoStore.list()` computes `start = page * limit`. Pages are
1-based, so the correct offset is `(page - 1) * limit`.

**Fix:** `start = (page - 1) * limit`.

---

## BUG-003 — completion_rate is truncated to a whole number

| Field | Value |
|---|---|
| **Severity** | Low |
| **Priority** | P2 |
| **Endpoint** | `GET /todos/stats` |
| **Found by** | TC-050 (`test_completion_rate_is_precise`, `test_stats_mixed`) |
| **Status** | Fixed |

**Steps to reproduce**

1. Create 3 todos, mark 1 done.
2. `GET /todos/stats`.

**Expected:** `"completion_rate": 33.3`
**Actual:** `0` (integer division `done // total * 100` floors first, so any
completion below 100% of a whole number reports as 0 or a rounded-down int).

**Root cause:** floor division instead of true division.

**Fix:** `round(done / total * 100, 1)`.

---

## BUG-004 — GET /todos/stats crashes with 500 on an empty store

| Field | Value |
|---|---|
| **Severity** | High |
| **Priority** | P1 |
| **Endpoint** | `GET /todos/stats` |
| **Found by** | TC-051 (`test_stats_on_empty_store`, `test_stats_empty`) |
| **Status** | Fixed |

**Steps to reproduce**

1. Start with an empty store (fresh service).
2. `GET /todos/stats`.

**Expected:** `200` with `{"total": 0, "done": 0, "pending": 0, "completion_rate": 0.0}`
**Actual:** `500 Internal Server Error` — `ZeroDivisionError: division by zero`
in `TodoStore.stats()`.

**Root cause:** no guard for `total == 0` before dividing.

**Fix:** early-return zeros when the store is empty.

---

## Verification

After the fixes, the full suite passes (see `test-run-fixed.log` +
coverage report). Every bug above is covered by a regression test that
failed before the fix and passes after — the suite cannot silently regress.
