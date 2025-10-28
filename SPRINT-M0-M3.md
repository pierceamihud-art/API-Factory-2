# Sprint Plan: M0 → M3 (Oneshot sprint)

Goal: finish stabilization (M0), model-adapter plumbing (M1), safety work (M2), and CI/tests (M3) so MVP is ready for early production testing.

Order: M0 → M1 → M2 → M3 (chronological order)

Quick status (from local run):
- Tests: 38 passed locally (good green baseline).
- CI workflow: `.github/workflows/ci.yml` exists and runs matrix for memory/redis.
- Rate limiter: `app/rate_limiter.py` supports `memory` and `redis` stores.
- Model adapter: `app/model_adapter.py` provides a simulated client fallback.
- SafeNow.env.example: present and contains example values.

Sprint checklist (PR-sized tasks)

M0 — Project stabilization & docs
- [x] Verify `requirements.txt` pinned versions. (done)
- [x] Ensure `SafeNow.env.example` present and up-to-date. (done)
- [ ] Add a short `CONTRIBUTING.md` with dev setup and test commands.
- [ ] Add a lightweight `CODE_OF_CONDUCT.md` (if desired for community).
- [ ] Small cleanups: fix DeprecationWarnings in `app/data_retention.py` (datetime.utcnow -> timezone-aware) — tiny PR.

M1 — Hardened MVP + model adapter
- [x] Adapter file present with simulated fallback.
- [ ] Add an interface contract test for the adapter (happy-path + simulated client). Create `tests/test_model_adapter.py`.
- [ ] Add feature-flag example via env `ENABLE_REAL_MODEL=true` to toggle real client usage.

M2 — Safety & policy automation
- [x] Memory/Redis limiter and tests exist.
- [ ] Add CI job matrix that exercises `RATE_LIMIT_STORE=redis` (already present) and confirms Redis service is up — check service declaration and make redis wait step robust.
- [ ] Add a small integration test that verifies rate limiting behavior in async concurrency (optional).
- [ ] Add a placeholder content-classifier hook (simple API) to allow swapping in a classifier later.

M3 — Tests & CI
- [x] `.github/workflows/ci.yml` exists and runs lint + tests.
- [ ] Improve CI: cache pip installs (speedup), ensure Redis service start step uses `services` properly and wait-for readiness; optionally add coverage reporting.
- [ ] Add a `make test` target or ensure `Makefile` has a `test` target (Makefile exists; consider linking to pytest).

Acceptance criteria
- All tests pass locally and in CI.
- README and `SafeNow.env.example` clearly document how to run tests and enable Redis-backed limiter.
- Adapter contract test passes w/ simulated client.
- CI matrix includes memory+redis and completes successfully.

Small low-risk PRs I can make now (pick any):
1. Add `CONTRIBUTING.md` and `SPRINT-M0-M3.md` (this file).
2. Add `tests/test_model_adapter.py` (unit tests for adapter simulated behavior).
3. Fix datetime deprecation warnings in `app/data_retention.py` and add test to assert no warnings.
4. Improve CI caching and Redis readiness in `.github/workflows/ci.yml`.

Next steps I will take if you confirm "go":
- Create PRs for items 1 and 2, run tests, and report results.
- Optionally implement item 3 (small code change + tests) and rerun tests.

Notes:
- The codebase already implements much of M0–M3; this sprint focuses on small cleanups, tests, and docs to harden the MVP for CI and early production.

