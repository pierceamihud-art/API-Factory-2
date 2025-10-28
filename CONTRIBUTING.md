# Contributing to API-Factory

Thank you for your interest in contributing!

## Quickstart (local dev)

1. Clone the repo and open in VS Code (dev container recommended).
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   . .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Copy `SafeNow.env.example` to `SafeNow.env` and fill in any secrets (do not commit secrets).
4. Run the dev server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. Run tests:
   ```bash
   pytest -q
   ```

## Making changes
- Please follow PEP8 and use `ruff` for linting.
- Add or update tests for new features and bugfixes.
- Run all tests before submitting a PR.
- For rate limiter changes, test both `memory` and `redis` modes.
- For model adapter changes, ensure simulated and real client paths are tested.

## Submitting PRs
- Fork the repo and create a feature branch.
- Open a pull request with a clear description of your changes.
- Ensure CI passes (lint + tests).

## Contact
- For questions, open an issue or contact the maintainers listed in `README.md`.
