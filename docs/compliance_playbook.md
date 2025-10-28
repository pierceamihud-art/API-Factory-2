# Compliance Playbook

This playbook summarizes the minimum compliance steps required to launch the API-Factory MVP into a production environment. Expand each section with your legal, privacy, and security teams before moving beyond pilot.

## 1. Governance Overview
- **Owners:** CISO (security), DPO (privacy), General Counsel (legal), Head of Engineering (technical controls).
- **Scope:** API inputs/outputs, audit logs, stored conversation snippets, API keys, billing metadata.
- **Frequency:** Quarterly compliance review; monthly audit log review; annual penetration test.

## 2. Regulatory Alignment
| Regulation | Applicability | Required Actions |
| --- | --- | --- |
| GDPR / UK GDPR | Users in EU/UK or processing EU data | Appoint DPO, document lawful basis, honor DSAR requests. |
| CCPA / CPRA | California residents | Provide opt-out mechanism, update privacy notice, establish data deletion workflow. |
| HIPAA (if health data) | Only if onboarding covered entities | Sign BAAs, isolate PHI, implement HIPAA safeguards. |
| SOC 2 (Type II) | Target certification | Establish control matrix, perform readiness assessment.

## 3. Data Handling Controls
- **Data classification:** Map incoming payloads to `PrivacyTier` levels (restricted / sensitive require enhanced consent).
- **Access controls:** Enforce RBAC for administrative endpoints; log all access in audit trail.
- **Encryption:** TLS 1.2+ for transport, encrypted storage for audit trail persistence (S3 with SSE or database with encryption at rest).
- **Retention:** Align with `RetentionPolicy` settings; document purge schedule; require justification for permanent retention.

## 4. Audit & Logging
- Ensure `AUDIT_LOG_PATH` is configured in production (points to append-only storage or log aggregator).
- Enable `LOG_REDACT_PII=true` to mask sensitive PII before logs leave the process.
- Schedule weekly integrity verification of audit hashes; export logs to long-term storage (e.g., SIEM).

## 5. Incident Response Checklist
1. Detect anomaly via metrics or audit trail.
2. Contain by revoking affected API keys and pausing canary deployment.
3. Investigate using audit log persistence and rate limiter history.
4. Notify stakeholders (legal, security, impacted customers) within SLA.
5. Eradicate root cause, document remediation, update runbooks.

## 6. Change Management
- Require PR review for policy files (`app/privacy.py`, `app/security.py`, `app/legal.py`).
- Maintain `docs/canary.md` as deployment SOP; sign-off from compliance before scaling beyond canary.
- Update this playbook when new integrations (billing, third-party LLM) are introduced.

## 7. Evidence Collection
- Store compliance evidence (policies, audits, training) in a secured repository.
- Attach CI artifacts (lint, tests, coverage) to releases for traceability.
- Capture consent records and retention justifications for high-risk data requests.

## 8. Launch Readiness Gate
- [ ] All env vars set (`AUDIT_LOG_PATH`, `LOG_REDACT_PII`, `ENABLE_REAL_MODEL` if applicable).
- [ ] Canary deployment completed with metrics & logs monitored for 24 hours.
- [ ] Audit integrity check passes with persisted logs.
- [ ] Legal + security sign-off recorded in issue tracker.

---
**TODOs for future sprints:** automate DSAR exports, integrate with centralized GRC platform, add automated privacy risk scoring.
