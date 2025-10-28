# ROADMAP

This file summarizes the E2E roadmap for API-Factory (MVP → Production). See README for quick start.

M0 — Project stabilization & docs
- Lock deps, add README, `SafeNow.env.example`, tidy code.

M1 — Hardened MVP + model adapter
- Add `app/models/adapter.py` to plumb in Claude Sonnet or other providers behind a feature flag.

M2 — Safety & policy automation
- Content classifier, Redis-backed rate limiter, env-configurable guardrails.

M3 — Tests & CI
- GitHub Actions to run lint, tests, build Docker image.

M4 — Observability & production readiness
- Prometheus metrics, structured logging, readiness checks.

M5 — Canary / rollout & scaling
- Container registry, k8s manifests, canary rollout.

M6 — Compliance & governance
- PII handling, audit logs, compliance checklist.
