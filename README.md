# Portfolio Project: Software Testing — Todo API

การทดสอบซอฟต์แวร์ (Software Testing) ครบกระบวนการ QA บน REST API จริง:
ออกแบบเทสต์ → เขียนเทสต์อัตโนมัติ → **จับบั๊กจริง 4 ตัว** → เขียน Bug Report → แก้ไข →
พิสูจน์ด้วย Regression Test → รายงาน Coverage

**สถานะ:** ![CI](https://github.com/Spcpi/todo-api-testing-portfolio/actions/workflows/ci.yml/badge.svg)
· 34 tests · 99% coverage

## What's inside

| Path | Description |
|---|---|
| `app/` | FastAPI Todo API (target under test) — in-memory store, 6 endpoints |
| `tests/test_unit_storage.py` | Unit tests: pagination & stats logic |
| `tests/test_api.py` | Integration/API tests: every endpoint + validation boundaries |
| `docs/test-plan.md` | Test plan: objectives, scope, strategy, entry/exit criteria |
| `docs/test-cases.md` | 27 test cases (TC-001..TC-052) with steps & expected results |
| `docs/bug-reports.md` | **4 bug reports** found by the suite, with root causes & fixes |
| `test-run-buggy.log` | Evidence: failing run **before** fixes (11 failed) |
| `test-run-fixed.log` | Evidence: green run **after** fixes (34 passed) |

## Bugs found by the tests

| ID | Severity | Summary |
|---|---|---|
| BUG-001 | Medium | `DELETE /todos/{id}` on unknown id returns 200, not 404 |
| BUG-002 | High | Pagination off-by-one — page 1 skips the first `limit` items |
| BUG-003 | Low | `completion_rate` truncated by integer division (33.3 → 0) |
| BUG-004 | High | `GET /todos/stats` crashes 500 on empty store (ZeroDivisionError) |

Full detail: `docs/bug-reports.md`.

## Tech stack

- Python 3.13, FastAPI, Pydantic
- pytest + pytest-cov (unit & integration via FastAPI `TestClient`)
- GitHub Actions CI (runs the suite on every push, Python 3.12 + 3.13)

## How to run

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Windows
# source .venv/bin/activate && pip install -r requirements.txt  # macOS/Linux
.venv/Scripts/python -m pytest --cov=app --cov-report=term-missing
```

Start the API locally:

```bash
.venv/Scripts/python -m uvicorn app.main:app --reload
# Swagger UI: http://127.0.0.1:8000/docs
```

## Process (what this portfolio demonstrates)

1. **Test plan first** — scope, risk, exit criteria (`docs/test-plan.md`).
2. **Design test cases from the contract** — happy path, boundaries
   (title length 200/201, priority 1–5, page/limit bounds), negatives
   (unknown ids, malformed input): `docs/test-cases.md`.
3. **Automate** — every test case maps to a pytest test (traceability below).
4. **Run → found 11 failing tests exposing 4 distinct bugs** → wrote formal
   bug reports with severity, repro steps, root cause, and fix.
5. **Fixed & verified** — same suite re-run: 34/34 green, 99% coverage.

## Test traceability (TC ↔ pytest)

| Test case | pytest node |
|---|---|
| TC-001..006 | `tests/test_api.py::TestCreateTodo` |
| TC-010..015 | `tests/test_api.py::TestListTodos` (+ unit pagination in `TestStorePagination`) |
| TC-020..022 | `tests/test_api.py::TestGetTodo` |
| TC-030..034 | `tests/test_api.py::TestPatchTodo` |
| TC-040..042 | `tests/test_api.py::TestDeleteTodo` |
| TC-050..052 | `tests/test_api.py::TestStats` + `tests/test_unit_storage.py::TestStoreStats` |

## Author

Supitsara — [github.com/Spcpi](https://github.com/Spcpi)
