# Test Cases — Todo API v1.0.0

Legend: TC-xxx = test-case id · P = Priority (P1 critical → P3 minor)

Execution result (after bug fixes, `test-run-fixed.log`): **all test cases Pass**.
Initial run (`test-run-buggy.log`): TC-011, TC-012, TC-013, TC-041, TC-042,
TC-050, TC-051 **Failed** → exposed BUG-001..004 (see `bug-reports.md`), which
were fixed and re-verified.

## Module: POST /todos

| ID | Title | Priority | Precondition | Steps | Expected result | Result |
|---|---|---|---|---|---|---|
| TC-001 | Create todo with valid payload | P1 | store empty | POST `{"title":"buy milk","priority":2}` | 201; body has id=1, done=false, title/priority echoed; created_at is ISO-8601 | |
| TC-002 | Create todo — title at max length (200) | P2 | — | POST with 200-char title | 201 | |
| TC-003 | Create todo — title too long (201) | P2 | — | POST with 201-char title | 422 | |
| TC-004 | Create todo — missing title | P1 | — | POST `{}` | 422 | |
| TC-005 | Create todo — priority out of range (0 / 6) | P2 | — | POST priority=0, then 6 | 422 both | |
| TC-006 | Create todo — priority default = 1 | P3 | — | POST without priority | 201, priority=1 | |

## Module: GET /todos

| ID | Title | Priority | Precondition | Steps | Expected result | Result |
|---|---|---|---|---|---|---|
| TC-010 | List empty store | P2 | store empty | GET /todos | 200; items=[], total=0, has_next=false | |
| TC-011 | List returns created todos | P1 | ≥2 todos | GET /todos | 200; items contain them; total matches | |
| TC-012 | Pagination — page 1 shows first N | P1 | 7 todos | GET /todos?limit=5 | items are ids 1–5; page=1; has_next=true | |
| TC-013 | Pagination — page 2 shows next N | P1 | 7 todos | GET /todos?limit=5&page=2 | items are ids 6–7; has_next=false | |
| TC-014 | Pagination — invalid page (0) | P3 | — | GET /todos?page=0 | 422 | |
| TC-015 | Pagination — invalid limit (0, 101) | P3 | — | GET /todos?limit=0 / 101 | 422 | |

## Module: GET /todos/{id}

| ID | Title | Priority | Precondition | Steps | Expected result | Result |
|---|---|---|---|---|---|---|
| TC-020 | Get existing todo | P1 | todo id=1 exists | GET /todos/1 | 200; full body | |
| TC-021 | Get unknown id → 404 | P1 | id absent | GET /todos/999 | 404, detail="todo not found" | |
| TC-022 | Get non-numeric id → 422 | P3 | — | GET /todos/abc | 422 | |

## Module: PATCH /todos/{id}

| ID | Title | Priority | Precondition | Steps | Expected result | Result |
|---|---|---|---|---|---|---|
| TC-030 | Mark done | P1 | todo exists | PATCH `{"done":true}` | 200; done=true; title unchanged | |
| TC-031 | Rename | P2 | todo exists | PATCH `{"title":"new"}` | 200; title=new | |
| TC-032 | Partial update keeps other fields | P2 | todo with priority=3 | PATCH done only | priority stays 3 | |
| TC-033 | PATCH unknown id → 404 | P1 | id absent | PATCH any | 404 | |
| TC-034 | PATCH invalid priority (6) | P2 | todo exists | PATCH `{"priority":6}` | 422 | |

## Module: DELETE /todos/{id}

| ID | Title | Priority | Precondition | Steps | Expected result | Result |
|---|---|---|---|---|---|---|
| TC-040 | Delete existing todo | P1 | todo exists | DELETE /todos/1 | 200, deleted=true; subsequent GET → 404 | |
| TC-041 | Delete unknown id → 404 | P1 | id absent | DELETE /todos/999 | **404**, deleted=false | |
| TC-042 | Delete twice → second is 404 | P2 | todo deleted | DELETE again | 404 | |

## Module: GET /todos/stats

| ID | Title | Priority | Precondition | Steps | Expected result | Result |
|---|---|---|---|---|---|---|
| TC-050 | Stats — mixed done/pending | P1 | 3 todos, 1 done | GET /todos/stats | total=3, done=1, pending=2, completion_rate=33.3 | |
| TC-051 | Stats — empty store | P1 | store empty | GET /todos/stats | 200; total=0, done=0, pending=0, completion_rate=0.0 | |
| TC-052 | Stats — all done | P2 | 4 todos, all done | GET /todos/stats | completion_rate=100.0 | |

## Traceability

Every TC above maps to a pytest test id in `tests/` — see the mapping table
in README.md (section "Test traceability").
