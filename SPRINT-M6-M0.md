# Oneshot Sprint Plan (M6 → M0) — 30% Turbo Build

Goal: deliver the most impactful 30% of work across all milestones (M6 down to M0) that unblocks the end-to-end MVP launch. This sprint focuses on high-leverage compliance, rollout, observability, CI, safety, model integration, and stabilization tasks.

## Snapshot of Milestone Status
| Milestone | Theme | Current Status | 30% Turbo Focus |
| --- | --- | --- | --- |
| M6 | Compliance & Governance | Initial docs only (`compliance/` CSVs). No runtime enforcement. | Implement audit log persistence stub, add PII redaction log, author `docs/compliance_playbook.md` with actionable checklist. |
| M5 | Canary / Rollout & Scaling | K8s folder exists (needs manifests). CI builds/tests only. | Add `k8s/deployment.yaml`, `k8s/service.yaml`, `k8s/hpa.yaml` skeleton; extend CI to build image (push optional). |
| M4 | Observability & Production Readiness | Metrics/README/test added. | Add log structured formatter toggle and readiness probe integration note. |
| M3 | Tests & CI | Lint/tests run in GH Actions. | Add coverage report & caching to CI. |
| M2 | Safety & Policy Automation | Safety validators, Redis limiter. | Add placeholder classifier interface `app/safety_classifier.py` + wire env toggle. |
| M1 | Hardened MVP + Model Adapter | Model adapter fallback, tests. | Add config env `ENABLE_REAL_MODEL` + doc updates. |
| M0 | Stabilization & Docs | README, env example, contributing doc. | Ensure `ARCHITECTURE.md` references new modules; tidy lint warnings. |

## Sprint Backlog (ordered by impact)
1. **Compliance quick wins (M6)**
   - [ ] Create `docs/compliance_playbook.md` summarizing obligations, audit steps, and sign-off checklist.
   - [ ] Update `app/audit.py` (or new module) to support persistence hook (e.g., to file/DB) with TODO for production integration.
   - [ ] Add `LOG_REDACT_PII=true` env flag and implement simple redaction filter in `app/privacy.py` or logging middleware.

2. **Rollout foundations (M5)**
   - [ ] Add Kubernetes baseline manifests under `k8s/` (deployment, service, hpa) with placeholders for container image, resources, and canary label.
   - [ ] Update `.github/workflows/ci.yml` with optional Docker build step triggered via `BUILD_IMAGE=true` env (skip push unless registry secret present).
   - [ ] Document rollout procedure in `docs/canary.md` (prereqs, deploy, traffic split, rollback).

3. **Observability polish (M4)**
   - [ ] Add JSON logging option via `LOG_FORMAT=json` env (structure logs using `logging.Formatter` or `json_log_formatter`).
   - [ ] Document readiness probe integration and sample `kubectl` command in README or new doc.

4. **CI improvements (M3)**
   - [ ] Enable pip caching and test coverage in GitHub Actions (upload coverage artifact).
   - [ ] Add Ruff lint caching (use `actions/setup-python` cache or `actions/cache`).

5. **Safety extensibility (M2)**
   - [ ] Create `app/safety_classifier.py` with strategy interface; update `app/main.py` to invoke when `SAFETY_CLASSIFIER=on`.
   - [ ] Add targeted tests in `tests/test_safety_classifier.py` covering stub classifier.

6. **Model adapter toggles (M1)**
   - [ ] Add env var `ENABLE_REAL_MODEL=false` and guard `ModelAdapter` instantiation accordingly; document in README.
   - [ ] Provide sample config snippet at `SafeNow.env.example`.

7. **Docs & stabilization updates (M0)**
   - [ ] Refresh `ARCHITECTURE.md` with new components (compliance, classifier, k8s).
   - [ ] Ensure `Makefile` includes coverage and lint targets referencing new CI steps.

## Execution Order (One-shot sprint)
- Phase 1: Compliance + rollout tasks (M6 & M5) — unblock governance and deployment.
- Phase 2: Observability + CI (M4 & M3) — ensure visibility and automation keep pace.
- Phase 3: Safety + adapter + docs (M2 → M0) — finalize supporting modules and documentation.

## Definition of Done
- New docs (`docs/compliance_playbook.md`, `docs/canary.md`) created and referenced from README or ROADMAP.
- `k8s/` folder contains baseline manifests; CI optionally builds Docker image.
- Logging supports JSON format toggle; coverage artifacts generated in CI.
- Safety classifier stub wired behind env flag; tests pass (≥42 existing + new ones).
- Architecture and env example updated to reflect new knobs.

## Turbo Build Notes (30%)
- Focus on scaffolding and documentation + thin shims (no external integrations yet).
- Mark stubs with clear TODOs for future sprints (database, registry secrets, production-grade classification).
- Ensure all new features are guarded by env flags to keep default dev workflows stable.
