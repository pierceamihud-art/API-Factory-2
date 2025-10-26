# API-Factory Architecture (v1.0)

## High-Level Flow
User → [Admin Web] → [API CLI (Fastify Kernel)] → [Templates/Adapters] → [Upstreams]

## Components
- **API CLI (apps/api-cli):**
  - Fastify server
  - Middleware chain: API-key → Quota → Rate-limit → Validator → Handler → Logger
  - Routes: `/_api/healthz`, `/api/v1/...`
  - Stripe webhook listener

- **Admin Web (apps/admin-web):**
  - React + Vite
  - Features: Health check, API key CRUD, usage charts, logs tail, test console

- **Core Package (packages/core):**
  - `ok()` / `err()` response helpers
  - `newRequestId()`
  - Types for ApiSuccess/ApiError

- **Monetization Spine:**
  - Stripe Products (Plans), Prices, Customers
  - Webhooks → DB sync
  - API Keys table: id, user_id, key_hash, plan_id, quota, status

- **Templates:**
  - JSON blueprint → auto-scaffold endpoints + schemas
  - Pre-built packs: Hello, Data Proxy, KYC, Webhook Relay

- **Docs:**
  - OpenAPI 3.1 at `/docs`
  - Swagger UI (dev only)

## Non-Goals (v1)
- Multi-tenant marketplace
- On-prem deployment
- Arbitrary code injection per endpoint
