## Quick context for AI coding agents

- Repo purpose: small MVP API server that demonstrates guarded LLM-like behaviour (placeholder model) with safety guardrails and a per-key rate limiter.
- Core service: `app/main.py` — a FastAPI app exposing `/health` and `/predict`.
- Tests: `tests/test_app.py` uses `pytest` with `pytest-asyncio` and `httpx.AsyncClient`.

## Big-picture architecture (read these files)
- `app/main.py` — single-process FastAPI service. Contains:
  - env-configured guardrails (e.g. `MAX_INPUT_CHARS`, `RATE_LIMIT_*`, `API_KEY`, `PREDICT_TIMEOUT`).
  - in-memory sliding-window rate limiter (`_rate_table`) — per-process only, not clustered-safe.
  - profanity filter via `BAD_WORDS` set (MVP).
  - placeholder model call `_simulate_model_call` — replace with real model integration.
- `requirements.txt` and `Dockerfile` — pinned deps and container entrypoint (`uvicorn app.main:app`).
- `SafeNow.env` — environment file referenced by Docker/compose; used for sensitive values (API_KEY, LOG_LEVEL, etc.). It is intentionally not populated in the repo.

## Project-specific conventions and patterns
- Single-file app: add endpoints and business logic in `app/main.py` unless you refactor into modules.
- Guardrails are read from environment variables with sensible defaults; prefer adding new runtime knobs via env var + default.
- Safety-first decisions are explicit and lightweight (e.g., simple profanity list, input/output character caps, timeout guard on model calls). When changing these, update tests that assert these behaviours.
- Tests use `httpx.AsyncClient(app=app, base_url=...)` — mimic integration requests without network.

## Developer workflows and commands (how to build, run, test)
- Local venv + run (Make targets provided):
  - `make setup` — create venv and install deps
  - `make run` — run uvicorn with autoreload during dev
  - `make test` — run pytest
- Docker / containerized dev:
  - `make docker-build` — build `api-factory:mvp`
  - `make docker-up` / `make docker-down` — docker-compose up/down (reads `SafeNow.env`)
- Quick curl example (use the repo's default dev key):
  - curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -H "X-API-Key: devkey" -d '{"input": "hello"}'

## Integration points and where to change things
- Replace `_simulate_model_call` in `app/main.py` to call an LLM or model adapter. Keep the outer timeout (`PREDICT_TIMEOUT`) and output-size truncation logic.
- If you need a cluster/global rate limiter, replace `_rate_table` with Redis or another shared store and keep the same API-key-based keying.
- Environment keys of interest: `API_KEY`, `LOG_LEVEL`, `MAX_INPUT_CHARS`, `MAX_OUTPUT_CHARS`, `RATE_LIMIT_WINDOW`, `RATE_LIMIT_REQUESTS`, `PREDICT_TIMEOUT`.

## Tests and expectations
- Tests assert safety behaviours (missing API key -> 401, long input -> 413, profanity -> 400). When modifying guardrails, update tests in `tests/test_app.py`.
- Use `pytest -q` (via `make test`) after any change. Tests run synchronously against the FastAPI app using AsyncClient.

## Security & secrets
- `SafeNow.env` is the intended place for secrets. Do NOT commit API keys or secrets. In CI add env var equivalents instead.

## Examples to look at for patterns
- `app/main.py` — shows: dependency-based API key check (`get_api_key`), per-request logging, small async model stub.
- `tests/test_app.py` — shows how to structure async tests and expected status codes.

If anything is unclear or you want the instructions tailored for a CI runner or a multi-process/production setup (Redis rate limiter, real model adapter), tell me which area to expand.
