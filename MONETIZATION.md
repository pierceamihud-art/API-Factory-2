# API-Factory Monetization Spine (Audit Spec)

## Entities
- **Plan**: Free, Starter, Pro, Enterprise
- **API Key**: hashed, bound to plan
- **Usage Log**: endpoint, latency, status, timestamp

## Stripe Mapping
- Product ↔ Plan
- Customer ↔ User
- Webhooks:
  - `checkout.session.completed` → issue API key
  - `invoice.payment_failed` → suspend key
  - `subscription.deleted` → revoke key

## Enforcement Order
1. Validate API key
2. Check quota (monthly)
3. Check rate-limit (req/min)
4. Execute route
5. Log usage

## Error Codes
- `401 UNAUTHORIZED` → invalid key
- `403 FORBIDDEN` → expired/revoked key
- `429 TOO_MANY_REQUESTS` → rate-limit exceeded
- `402 PAYMENT_REQUIRED` → quota exceeded
