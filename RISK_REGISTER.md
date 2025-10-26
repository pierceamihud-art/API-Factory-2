# API-Factory Risk Register

## Top Risks
1. Monetization Slip → APIs not billable
   Mitigation: Build Stripe spine first

2. Auth Drift → inconsistent API-key enforcement
   Mitigation: central middleware

3. CI/CD Gap → manual deploys, higher error rates
   Mitigation: baseline GitHub Actions pipeline

4. Usage Metering Accuracy → over/under charging
   Mitigation: atomic counters + tests

5. Docs Drift → client confusion
   Mitigation: auto-generate OpenAPI from routes

6. PII Handling → compliance issues
   Mitigation: schema redaction + payload caps
