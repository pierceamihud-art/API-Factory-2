# API-Factory (Solo Project)

## Vision
API-Factory lets solo devs and small teams build **real-world-ready APIs** with
billing, auth, rate-limiting, logging, and docs already included.
Just describe the service → API-Factory generates the API + Admin + Stripe billing.

> 📊 **Progress Audit Available:** See [EXECUTIVE_SUMMARY.md](./EXECUTIVE_SUMMARY.md) for current project status  
> 📚 **Documentation Index:** See [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) for navigation guide

## Key Features
- 🔑 API key issuance, quotas, and rate-limits
- 💳 Stripe billing integration (plans, webhooks, auto key revoke/issue)
- 📜 Canonical JSON responses with request IDs
- 📊 Usage logs & metrics at `/_api/metrics`
- 📑 OpenAPI docs auto-generated
- 🖥️ Admin console: Keys, Plans, Logs, Test Console

## Quick Start

> ⚠️ **NOT YET FUNCTIONAL** – The commands below represent the target developer experience.  
> Monorepo structure and application code are not yet implemented.

```bash
# Planned (not yet working):
pnpm install
pnpm dev
# API: http://localhost:8787/_api/healthz
# Web: http://localhost:5173
```

**For Contributors:** See [PROGRESS_AUDIT.md](./PROGRESS_AUDIT.md) §8.1 for scaffolding instructions.

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

> ⚠️ **PROJECT PHASE: PLANNING & DOCUMENTATION**  
> This repository contains comprehensive planning artifacts but **no functional code yet**.  
> See [PROGRESS_AUDIT.md](./PROGRESS_AUDIT.md) for detailed status analysis.

### Implementation Status
- 🔴 API CLI baseline (`/_api/healthz`, `/hello/ping`, `/hello/echo`) – **NOT STARTED**
- 🔴 Admin web (Health + Ping integration) – **NOT STARTED**
- 🔴 Monetization spine (Stripe + keys) – **NOT STARTED**
- 🔴 Template packs (Data Proxy, KYC) – **NOT STARTED**
- 🔴 CI/CD pipelines – **NOT STARTED**

### Documentation Status
- ✅ Architecture design (ARCHITECTURE.md)
- ✅ Roadmap planning (ROADMAP.md)
- ✅ OpenAPI specification (OPENAPI.yaml)
- ✅ Governance framework (GUARDRAILS.md)
- ✅ Risk analysis (RISK_REGISTER.md)
- ✅ Monetization spec (MONETIZATION.md)

## License
Proprietary (internal use only)
