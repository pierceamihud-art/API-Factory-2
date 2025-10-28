# Sprint M4: Observability & Production Readiness

Goal: Ensure the API service is observable and ready for production rollout.

## Checklist
- [ ] Review and improve Prometheus metrics coverage (request count, latency, error types).
- [ ] Add/verify structured logging (JSON logs, log level config, error context).
- [ ] Add readiness/liveness endpoints (e.g., `/health`, `/admin/health/deep`).
- [ ] Document metrics and logging setup in README.
- [ ] Add tests for metrics and health endpoints.
- [ ] Ensure metrics are exposed for scraping (Prometheus config example).

## Acceptance Criteria
- All endpoints emit relevant metrics.
- Logs are structured and configurable by env.
- Health/readiness endpoints return correct status and check subsystems.
- README documents how to enable and scrape metrics.
- All new tests pass locally and in CI.

## Next Steps
- Review current metrics and logging code in `app/main.py` and `app/metrics.py`.
- Add missing metrics or logging improvements.
- Implement or improve readiness endpoints.
- Update README and add tests.
