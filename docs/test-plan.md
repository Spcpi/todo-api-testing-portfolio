# Test Plan — Todo API v1.0.0

| | |
|---|---|
| **Project** | Todo API (FastAPI, in-memory store) |
| **Version under test** | 1.0.0 (commit `main`) |
| **Author** | Supitsara (Spcpi) |
| **Date** | 2026-08-31 |
| **Test levels** | Unit (store logic), Integration/API (HTTP via FastAPI TestClient) |
| **Tools** | Python 3.13, pytest 8, pytest-cov, FastAPI TestClient |

## 1. Objectives

1. Verify every documented endpoint behaves according to its contract
   (status codes, response schema, side effects).
2. Verify input validation boundaries (title length, priority range,
   pagination bounds, unknown ids).
3. Verify aggregate statistics and pagination math.
4. Find, document, and regress real defects — this portfolio deliberately
   demonstrates **bugs found by tests → documented → fixed → re-tested**.

## 2. Scope

**In scope:** `POST /todos`, `GET /todos`, `GET /todos/{id}`,
`PATCH /todos/{id}`, `DELETE /todos/{id}`, `GET /todos/stats`,
and the `TodoStore` unit layer beneath them.

**Out of scope:** persistence (in-memory by design), auth, rate limiting,
concurrency, deployment.

## 3. Test strategy

- **Unit tests** target `TodoStore` directly — fast, isolate business math
  (pagination offsets, stats) from HTTP concerns.
- **Integration tests** drive the real FastAPI app through `TestClient`
  (in-process ASGI, real routing + validation) against a fresh store per
  test via dependency override.
- **Boundary / negative tests** cover invalid payloads and unknown ids.
- Coverage target: ≥ 90% of `app/`.

## 4. Entry / Exit criteria

- **Entry:** app imports cleanly; test suite runs end-to-end.
- **Exit:** all test cases Pass; documented bugs verified fixed with
  regression tests; coverage ≥ 90%.

## 5. Risks

| Risk | Mitigation |
|---|---|
| Shared state between tests | Fresh `TodoStore` per test (fixture isolation) |
| Time-dependent flakiness | Only assert ISO-format presence, not exact timestamps |
