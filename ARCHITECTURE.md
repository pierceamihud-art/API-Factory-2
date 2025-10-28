# ARCHITECTURE

High-level architecture for the API-Factory concept:

- Frontend: Next.js admin + docs
- Backend: FastAPI/Fastify microservices hosting APIs
- Shared packages: auth, billing, metrics, openapi composition
- Data stores: Postgres (metadata), Redis (rate limits, counters), optional Supabase backup for audit/API key/retention records
- Observability: Prometheus + Grafana, structured logs

This repo currently contains a FastAPI MVP with guardrails and a small router example.
