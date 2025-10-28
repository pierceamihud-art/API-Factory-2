# RISK REGISTER

Key risks and mitigations for API-Factory MVP:

- Risk: accidental secrets in repo — Mitigation: use `.env` files, add pre-commit checks.
- Risk: in-memory rate limiter not cluster-safe — Mitigation: Redis-backed limiter available.
- Risk: model returns unsafe content — Mitigation: output filters, human-in-the-loop, telemetry.
- Risk: billing errors — Mitigation: idempotent webhook handling and test harness.
