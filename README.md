# API-Factory (Solo Project)

## Vision
API-Factory lets solo devs and small teams build **real-world-ready APIs** with
billing, auth, rate-limiting, logging, and docs already included.
Just describe the service → API-Factory generates the API + Admin + Stripe billing.

## Key Features
- 🔑 API key issuance, quotas, and rate-limits
- 💳 Stripe billing integration (plans, webhooks, auto key revoke/issue)
- 📜 Canonical JSON responses with request IDs
- 📊 Usage logs & metrics at `/_api/metrics`
- 📑 OpenAPI docs auto-generated
- 🖥️ Admin console: Keys, Plans, Logs, Test Console

## Quick Start
```bash
pnpm install
pnpm dev
# API: http://localhost:8787/_api/healthz
# Web: http://localhost:5173
```

## Repo Layout
```
/ (repo root)
  ├─ apps/
  │   ├─ api-cli/       # Fastify server (core kernel + templates)
  │   └─ admin-web/     # Vite + React admin console
  ├─ packages/
  │   └─ core/          # shared utils, types, error helpers
  ├─ scripts/           # devops tools (verify, build, deploy)
  ├─ .env.example
  └─ README.md
```

## Current Status
- ✅ API CLI baseline (`/_api/healthz`, `/hello/ping`, `/hello/echo`)
- ✅ Admin web (Health + Ping integration)
- 🟡 Monetization spine (Stripe + keys) – **in progress**
- 🟡 Template packs (Data Proxy, KYC) – **in progress**
- 🔴 CI/CD pipelines – **not started**

## License
Proprietary (internal use only)
