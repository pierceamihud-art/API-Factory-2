# API-Factory Roadmap (v1.0)

> **Last Updated:** October 27, 2025  
> **Status:** See [PROGRESS_AUDIT.md](./PROGRESS_AUDIT.md) for detailed analysis

---

## Reality Check ⚠️

**Original Roadmap Status (from documentation):**
- Gate A: Foundation ✅ (claimed complete)
- Gate B: Dev Servers ✅ (claimed complete)
- Gate C: First Service ✅ (claimed complete)

**Actual Status (as of Oct 27, 2025):**
- Gate A: Foundation 🟡 (docs exist, code does not)
- Gate B: Dev Servers 🔴 (not started)
- Gate C: First Service 🔴 (not started)
- Gate D: Admin Web 🔴 (not started)
- Gate E: Packaging 🔴 (not started)
- Gate F: Monetization 🔴 (not started)

**Implementation Progress:** 0% (zero lines of production code)

See [IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md) for actionable tasks.

---

## Revised Stage Gates

### Gate A: Foundation (repo, env, README)
**Original Status:** ✅ Complete  
**Actual Status:** 🟡 Partially Complete  

**Completed:**
- ✅ Repository created
- ✅ Comprehensive documentation (README, ARCHITECTURE, etc.)
- ✅ LICENSE file
- ✅ Verification scripts (check-docs.mjs, verify-openapi.mjs)

**Missing:**
- ❌ Monorepo structure (apps/, packages/, scripts/)
- ❌ package.json + pnpm-workspace.yaml
- ❌ .env.example with real template
- ❌ .github/ workflows and templates
- ❌ .gitignore, .editorconfig
- ❌ TypeScript configuration

**Target Completion:** Week 1 (Phase 0 of IMPLEMENTATION_CHECKLIST.md)

---

### Gate B: Dev Servers (CLI + Vite, proxy)
**Original Status:** ✅ Complete  
**Actual Status:** 🔴 Not Started  

**Required Deliverables:**
- [ ] Fastify server running on port 8787
- [ ] Vite dev server running on port 5173
- [ ] Vite proxy configured to forward API requests
- [ ] Hot reload working for both API and Web
- [ ] `pnpm dev` command starts both servers

**Dependencies:** Gate A must be complete  
**Target Completion:** Week 1-2 (Phase 0-1 of IMPLEMENTATION_CHECKLIST.md)

---

### Gate C: First Service (ping/echo)
**Original Status:** ✅ Complete  
**Actual Status:** 🔴 Not Started  

**Required Deliverables:**
- [ ] `GET /_api/healthz` endpoint (200 OK with metadata)
- [ ] `GET /api/v1/hello/ping` endpoint (returns "pong")
- [ ] `POST /api/v1/hello/echo` endpoint (echoes request body)
- [ ] All responses match OPENAPI.yaml specification
- [ ] Integration tests for all 3 endpoints
- [ ] `verify-openapi.mjs` passes against running server

**Dependencies:** Gate B must be complete  
**Target Completion:** Week 2 (Phase 1 of IMPLEMENTATION_CHECKLIST.md)

---

### Gate D: Admin Web (keys, usage, logs)
**Original Status:** ⏳ In Progress  
**Actual Status:** 🔴 Not Started  

**Required Deliverables:**
- [ ] Health check dashboard (calls `/_api/healthz`)
- [ ] API test console (ping/echo forms)
- [ ] API key list view (read-only initially)
- [ ] Basic styling (Tailwind CSS or similar)
- [ ] Responsive layout (mobile-friendly)

**Dependencies:** Gate C must be complete  
**Target Completion:** Week 3-4 (Phase 1-3 of IMPLEMENTATION_CHECKLIST.md)

---

### Gate E: Packaging (CI/CD, Docker)
**Original Status:** ⏳ In Progress  
**Actual Status:** 🔴 Not Started  

**Required Deliverables:**
- [ ] `.github/workflows/guardrails.yml` (lint, test, typecheck)
- [ ] `.github/workflows/deploy.yml` (staging deployment)
- [ ] Dockerfile for API service
- [ ] docker-compose.yml for local development
- [ ] SBOM generation (CycloneDX)
- [ ] Code coverage reporting (Codecov)

**Dependencies:** Gate C must be complete  
**Target Completion:** Week 5-6 (Phase 4 of IMPLEMENTATION_CHECKLIST.md)

---

### Gate F: Monetization (Stripe + keys + quotas)
**Original Status:** ⏳ In Progress  
**Actual Status:** 🔴 Not Started  

**Required Deliverables:**
- [ ] Stripe SDK integrated
- [ ] API keys table in database
- [ ] API key middleware (validation + quota check)
- [ ] Rate limiting middleware
- [ ] Stripe webhook handler (checkout, invoice, subscription)
- [ ] Admin console for key management
- [ ] Usage logs table + metrics endpoint

**Dependencies:** Gate C must be complete  
**Target Completion:** Week 3-5 (Phase 2 of IMPLEMENTATION_CHECKLIST.md)

---

## Phase Rollout (Revised)

| Phase | Original Timeline | Revised Timeline | Deliverables | Status |
|-------|-------------------|------------------|--------------|--------|
| **Phase 0: Foundation** | N/A | **Week 1** | Monorepo scaffold, CI/CD bootstrap | 🔴 Not Started |
| **Phase 1: Kernel** | Weeks 1-2 | **Week 2** | 3 baseline endpoints, tests | 🔴 Not Started |
| **Phase 2: Monetization** | Weeks 2-3 | **Weeks 3-5** | Stripe + keys + quotas | 🔴 Not Started |
| **Phase 3: Templates** | Weeks 2-4 | **Week 4-5** | Template engine + packs | 🔴 Not Started |
| **Phase 4: Admin Features** | Weeks 4-5 | **Week 3-6** | Key mgmt, logs, charts | 🔴 Not Started |
| **Phase 5: Reliability** | Week 6 | **Week 5-7** | CI/CD, monitoring, security | 🔴 Not Started |
| **Phase 6: Polish** | N/A | **Week 7** | Docs, launch prep | 🔴 Not Started |

**Total Duration:** 6-7 weeks (solo developer, full-time)  
**Confidence Level:** 70% (ambitious but achievable with focus)

---

## Success Metrics

### Gate C (Revised)
- **TTFP (Time to First API Call):** < 5 minutes ⏱️
- **Endpoint Coverage:** 3/3 baseline endpoints ✅
- **Test Coverage:** ≥ 80% 🧪
- **CI Pipeline:** All checks passing ✅
- **Documentation Accuracy:** ≥ 95% 📚

### Launch (Gate F + Reliability)
- **≥ 90% auto-generated APIs pass smoke tests**
- **Churn on paid keys < 25% in 60 days**
- **p95 latency < 200ms**
- **Error rate < 1% under load**
- **First paying customer onboarded** 💰

---

## Critical Path Analysis

```
Week 1: Foundation Scaffolding (Gate A + B)
   ↓
Week 2: First Service Implementation (Gate C) ⭐ MILESTONE 1
   ↓
Week 3-5: Monetization Spine (Gate F) ⭐ MILESTONE 2
   ↓  ↘
Week 4-5: Template System (Gate D)
   ↓  ↙
Week 5-7: Reliability & CI/CD (Gate E) ⭐ MILESTONE 3
   ↓
Week 7: Launch Prep ⭐ MILESTONE 4
```

**Critical Path:** Foundation → First Service → Monetization → Reliability  
**Parallelizable:** Templates can start after First Service (doesn't block Monetization)

---

## Risk-Adjusted Timeline

**Optimistic (Everything Goes Well):** 6 weeks  
**Realistic (Normal Blockers):** 7-8 weeks  
**Pessimistic (Major Issues):** 10-12 weeks

**Key Risk Factors:**
1. Database schema design iteration (add 3-5 days)
2. Stripe webhook debugging (add 2-3 days)
3. Rate limiting accuracy tuning (add 2-3 days)
4. Security vulnerability remediation (add 1-5 days)

---

## Next Actions (This Week)

**Priority 1:** Complete Phase 0 (Foundation Scaffolding)
- [ ] Create monorepo structure
- [ ] Scaffold api-cli (Fastify)
- [ ] Scaffold admin-web (Vite + React)
- [ ] Create packages/core (helpers)
- [ ] Add CI/CD workflows
- [ ] Verify `pnpm dev` works end-to-end

**Target:** 8-12 hours of focused development  
**Owner:** Project maintainers  
**Review Date:** End of Week 1

---

**Roadmap Version:** 2.0 (Revised from v1.0)  
**Last Updated:** October 27, 2025  
**Next Review:** After Gate A completion (Week 1)
