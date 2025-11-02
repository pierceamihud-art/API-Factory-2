# API-Factory Implementation Checklist

> **Purpose:** Track the transition from planning phase to working MVP  
> **Last Updated:** October 27, 2025  
> **Target Completion:** Gate C (First Service Live)

---

## Phase 0: Foundation Scaffolding (72 Hours) 🚨 CRITICAL PATH

### Monorepo Structure
- [ ] Create directory structure: `apps/`, `packages/`, `scripts/`
- [ ] Create `pnpm-workspace.yaml` with workspace configuration
- [ ] Create root `package.json` with workspace dependencies
- [ ] Create `tsconfig.base.json` for shared TypeScript config
- [ ] Create `.gitignore` (node_modules, dist, .env, etc.)
- [ ] Create `.editorconfig` for consistent formatting
- [ ] Rename `SafeNow.env` to `.env.example` with real template values

### API CLI Scaffolding (apps/api-cli)
- [ ] Create `apps/api-cli/package.json`
- [ ] Install Fastify + TypeScript dependencies
- [ ] Create `apps/api-cli/src/index.ts` (server entry point)
- [ ] Create `apps/api-cli/tsconfig.json`
- [ ] Add `/_api/healthz` endpoint (matches OPENAPI.yaml)
- [ ] Add `/api/v1/hello/ping` endpoint (matches OPENAPI.yaml)
- [ ] Add `/api/v1/hello/echo` endpoint (matches OPENAPI.yaml)
- [ ] Create `apps/api-cli/tests/` directory
- [ ] Add integration test for healthz endpoint
- [ ] Verify server starts with `pnpm --filter api-cli dev`

### Admin Web Scaffolding (apps/admin-web)
- [ ] Create `apps/admin-web/package.json`
- [ ] Initialize Vite + React + TypeScript project
- [ ] Create `apps/admin-web/src/App.tsx` (main component)
- [ ] Create `apps/admin-web/src/main.tsx` (entry point)
- [ ] Create `apps/admin-web/index.html`
- [ ] Add HealthCheck component (calls `/_api/healthz`)
- [ ] Configure Vite proxy to `localhost:8787`
- [ ] Verify admin web starts with `pnpm --filter admin-web dev`

### Core Package (packages/core)
- [ ] Create `packages/core/package.json`
- [ ] Create `packages/core/src/response.ts` (ok/err helpers)
- [ ] Create `packages/core/src/types.ts` (ApiSuccess/ApiError)
- [ ] Create `packages/core/src/utils.ts` (newRequestId)
- [ ] Create `packages/core/tsconfig.json`
- [ ] Add unit tests for response helpers
- [ ] Export all public APIs from `packages/core/src/index.ts`

### CI/CD Bootstrap
- [ ] Create `.github/workflows/guardrails.yml`
  - [ ] Lint job (ESLint)
  - [ ] Type check job (TypeScript)
  - [ ] Test job (Vitest)
  - [ ] Documentation job (check-docs.mjs, verify-openapi.mjs)
- [ ] Create `.github/pull_request_template.md` (SSF checklist)
- [ ] Create `.github/CODEOWNERS`
- [ ] Create `.github/dependabot.yml`
- [ ] Create `.github/ISSUE_TEMPLATE/bug_report.md`
- [ ] Create `.github/ISSUE_TEMPLATE/feature_request.md`

### Documentation Updates
- [ ] Update README.md with accurate status ✅ (COMPLETED)
- [ ] Create CHANGELOG.md
- [ ] Expand CONTRIBUTING.md with SSF examples
- [ ] Add PROGRESS_AUDIT.md ✅ (COMPLETED)
- [ ] Add this IMPLEMENTATION_CHECKLIST.md ✅ (COMPLETED)

### Verification (Gate A Complete)
- [ ] Run `pnpm install` successfully from repo root
- [ ] Run `pnpm --filter api-cli dev` successfully
- [ ] Run `pnpm --filter admin-web dev` successfully
- [ ] Visit `http://localhost:8787/_api/healthz` → 200 OK
- [ ] Visit `http://localhost:5173` → Admin web loads
- [ ] Run `pnpm test` → All tests pass
- [ ] Push branch → CI pipeline runs and passes

**Estimated Effort:** 8-12 hours (1-2 days for experienced developer)

---

## Phase 1: First Service (Gate C) – Week 1

### API Implementation
- [ ] Implement canonical JSON response format (per ARCHITECTURE.md)
- [ ] Add request ID generation to all responses
- [ ] Add structured logging (Winston or Pino)
- [ ] Add error handling middleware
- [ ] Add CORS configuration
- [ ] Add health check with service metadata (version, uptime)

### Testing
- [ ] Integration test for `/ping` endpoint
- [ ] Integration test for `/echo` endpoint
- [ ] Test request ID uniqueness
- [ ] Test error response format
- [ ] Test CORS headers
- [ ] Achieve 80%+ code coverage on API routes

### Admin Web
- [ ] Create Ping Test page
- [ ] Create Echo Test page (form + response display)
- [ ] Add basic styling (Tailwind CSS recommended)
- [ ] Display API health status on dashboard

### OpenAPI Validation
- [ ] Run `verify-openapi.mjs` against live server
- [ ] Fix any drift between spec and implementation
- [ ] Add automated OpenAPI compliance test to CI

### Documentation
- [ ] Update README Quick Start with working commands
- [ ] Add API usage examples to README
- [ ] Document environment variables in .env.example
- [ ] Add troubleshooting section to CONTRIBUTING.md

**Gate C Success Criteria:**
- [ ] All 3 baseline endpoints functional
- [ ] Admin web can interact with all endpoints
- [ ] All tests passing in CI
- [ ] TTFP (Time to First API Call) < 5 minutes
- [ ] Documentation matches reality

**Estimated Effort:** 16-24 hours (2-3 days)

---

## Phase 2: Monetization Spine (Gate F) – Weeks 2-3

### Stripe Integration
- [ ] Install Stripe SDK (`stripe` npm package)
- [ ] Create Stripe account (test mode)
- [ ] Configure Products (Free, Starter, Pro, Enterprise)
- [ ] Configure Prices for each product
- [ ] Add Stripe API keys to `.env.example`

### API Key Management
- [ ] Design API keys schema (id, user_id, key_hash, plan_id, quota, status)
- [ ] Choose database (PostgreSQL recommended)
- [ ] Create migration: `api_keys` table
- [ ] Implement API key generation (secure random + hashing)
- [ ] Add API key middleware (validation)
- [ ] Add quota check middleware
- [ ] Add rate-limiting middleware (using `express-rate-limit`)

### Usage Logging
- [ ] Create migration: `usage_logs` table
- [ ] Implement usage logger (endpoint, latency, status, timestamp)
- [ ] Add usage metrics endpoint (`/_api/metrics`)
- [ ] Configure log rotation/retention policy

### Stripe Webhooks
- [ ] Create webhook endpoint (`/webhooks/stripe`)
- [ ] Handle `checkout.session.completed` → issue API key
- [ ] Handle `invoice.payment_failed` → suspend key
- [ ] Handle `subscription.deleted` → revoke key
- [ ] Add webhook signature verification
- [ ] Add webhook event logging

### Error Codes (per MONETIZATION.md)
- [ ] Implement 401 UNAUTHORIZED (invalid key)
- [ ] Implement 403 FORBIDDEN (expired/revoked key)
- [ ] Implement 429 TOO_MANY_REQUESTS (rate-limit exceeded)
- [ ] Implement 402 PAYMENT_REQUIRED (quota exceeded)

### Testing
- [ ] Unit tests for API key hashing/validation
- [ ] Integration tests for protected endpoints
- [ ] Mock Stripe webhook tests
- [ ] Rate-limiting tests
- [ ] Quota enforcement tests

### Admin Web Updates
- [ ] API key list page
- [ ] API key creation form
- [ ] API key revocation button
- [ ] Usage logs viewer
- [ ] Quota/rate-limit display

**Estimated Effort:** 40-60 hours (1-2 weeks)

---

## Phase 3: Template System (Gate D) – Week 4

### Template Engine
- [ ] Design template JSON schema
- [ ] Create template loader (read from `templates/`)
- [ ] Auto-generate routes from template
- [ ] Auto-generate OpenAPI spec from template
- [ ] Add template validation

### Pre-built Templates
- [ ] Hello template (ping, echo) – already implemented
- [ ] Data Proxy template (forward requests to upstream)
- [ ] KYC template (identity verification stub)
- [ ] Webhook Relay template (receive + forward webhooks)

### Admin Web Updates
- [ ] Template selector UI
- [ ] Template deployment wizard
- [ ] Generated API preview

### Documentation
- [ ] Template authoring guide
- [ ] Template JSON schema documentation
- [ ] Example templates repository

**Estimated Effort:** 24-40 hours (3-5 days)

---

## Phase 4: Reliability & Operations (Gate E) – Week 5-6

### CI/CD Enhancements
- [ ] Add code coverage reporting (Codecov)
- [ ] Add security scanning (Snyk or GitHub Dependabot alerts)
- [ ] Generate SBOM (CycloneDX format)
- [ ] Add automated deployment to staging
- [ ] Add smoke tests for deployed environments

### Monitoring & Observability
- [ ] Add structured logging (JSON format)
- [ ] Add metrics export (Prometheus format)
- [ ] Add error tracking (Sentry or similar)
- [ ] Add uptime monitoring (UptimeRobot or similar)
- [ ] Create runbook for common issues

### Performance
- [ ] Add response time tracking
- [ ] Optimize database queries
- [ ] Add caching layer (Redis)
- [ ] Load testing (k6 or Artillery)
- [ ] Set performance budgets (p95 latency < 200ms)

### Security Hardening
- [ ] Enable HTTPS in production
- [ ] Add helmet.js middleware
- [ ] Implement rate limiting per IP
- [ ] Add request validation (JSON schema)
- [ ] Security audit of dependencies
- [ ] Penetration testing (basic)

### Documentation
- [ ] Production deployment guide
- [ ] Operational runbook
- [ ] Incident response plan
- [ ] Performance tuning guide

**Estimated Effort:** 40-60 hours (1-2 weeks)

---

## Phase 5: Polish & Launch Prep – Week 7

### Final Testing
- [ ] Full regression test suite
- [ ] Browser compatibility testing (admin web)
- [ ] Mobile responsiveness testing (admin web)
- [ ] Accessibility audit (WCAG 2.1 Level AA)
- [ ] Load testing (1000 req/s)

### Documentation
- [ ] API reference (complete)
- [ ] SDK documentation (if applicable)
- [ ] Getting Started tutorial
- [ ] Video walkthrough (optional)
- [ ] FAQ section

### Marketing Assets
- [ ] Feature comparison table
- [ ] Pricing calculator
- [ ] Case studies / examples
- [ ] Blog post announcing launch

### Legal & Compliance
- [ ] Terms of Service
- [ ] Privacy Policy
- [ ] SLA definition
- [ ] GDPR compliance checklist (if applicable)

**Estimated Effort:** 20-30 hours (3-4 days)

---

## Total Estimated Timeline

| Phase | Duration | Effort (Hours) | Dependencies |
|-------|----------|----------------|--------------|
| **Phase 0** | 1-2 days | 8-12 | None (start immediately) |
| **Phase 1** | 2-3 days | 16-24 | Phase 0 complete |
| **Phase 2** | 1-2 weeks | 40-60 | Phase 1 complete |
| **Phase 3** | 3-5 days | 24-40 | Phase 1 complete (can parallel with Phase 2) |
| **Phase 4** | 1-2 weeks | 40-60 | Phase 2 complete |
| **Phase 5** | 3-4 days | 20-30 | All phases complete |
| **TOTAL** | **6-7 weeks** | **148-226 hours** | Sequential + some parallel work |

**Solo Developer:** 6-7 weeks full-time  
**Small Team (2-3 devs):** 3-4 weeks with parallelization  

---

## Success Metrics (Revisited)

### Gate C (First Service) – Target for Phase 1
- ✅ Time to First API Call < 5 minutes
- ✅ 3/3 baseline endpoints functional
- ✅ 80%+ test coverage
- ✅ CI pipeline green
- ✅ Documentation accuracy > 95%

### Gate F (Monetization) – Target for Phase 2
- ✅ Stripe integration functional
- ✅ API key issuance automated
- ✅ Quota enforcement working
- ✅ Rate limiting working
- ✅ Payment webhook handling tested

### Launch Readiness – Target for Phase 5
- ✅ Production deployment successful
- ✅ Monitoring dashboards live
- ✅ < 1% error rate under load
- ✅ p95 latency < 200ms
- ✅ Documentation complete
- ✅ Security audit passed

---

## How to Use This Checklist

1. **Daily Standup:** Review in-progress items, update status
2. **Weekly Review:** Calculate % complete per phase, adjust timeline
3. **Blockers:** Flag items that cannot start due to dependencies
4. **Velocity Tracking:** Measure completed items per day/week
5. **Risk Management:** If Phase 0 takes > 3 days, escalate planning issues

**Recommended Tool:** GitHub Projects board with columns for each phase

---

## Next Steps (Starting Now)

**Priority 1 (This Week):** Complete Phase 0 Foundation Scaffolding
1. Clone this repo to local development environment
2. Create monorepo structure (30 minutes)
3. Scaffold api-cli with Fastify (2 hours)
4. Scaffold admin-web with Vite + React (2 hours)
5. Create core package with helpers (1 hour)
6. Set up CI/CD workflows (2 hours)
7. Verify full development flow works (1 hour)

**Priority 2 (Next Week):** Complete Phase 1 Gate C
1. Implement 3 baseline endpoints
2. Write integration tests
3. Build admin web test console
4. Update all documentation

**Priority 3 (Weeks 3-4):** Complete Phase 2 Monetization Spine
1. Integrate Stripe
2. Implement API key middleware
3. Add usage logging

---

**Checklist Version:** 1.0  
**Owned By:** Project maintainers  
**Review Cadence:** Weekly (update % complete, adjust estimates)  
