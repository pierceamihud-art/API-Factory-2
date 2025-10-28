# Canary Deployment Playbook

This document describes a simple canary deployment process for API-Factory.

Prerequisites
- Cluster with ingress or service routing that supports weighted traffic (e.g., istio/traefik/nginx annotations or manual split via service updates).
- CI that can build and push `ghcr.io/your-org/api-factory:canary` image.

Steps
1. Build and push canary image (CI or local):
   - `docker build -t ghcr.io/your-org/api-factory:canary .`
   - `docker push ghcr.io/your-org/api-factory:canary`
2. Apply canary deployment manifest:
   - `kubectl apply -f k8s/deployment-canary.yaml`
3. Route a small % of traffic to canary (depends on platform):
   - If using Service mesh, create route rule to send 5-10% to `track: canary`.
   - If using simple Service, deploy canary with separate service and update ingress weights.
4. Monitor metrics and logs for 10–30 minutes.
   - Check `/metrics` for error spikes and latency.
   - Check audit logs for anomalies.
5. Promote to stable:
   - If healthy, update `k8s/deployment.yaml` image to canary tag and increase replicas.
   - Delete canary deployment.
6. Rollback:
   - Delete canary deployment and revert image in stable deployment if issues found.

Notes
- Keep canary low risk: reduced replicas, debug logging enabled, isolated feature flags.
- Automate smoke tests in CI to run against canary before promotion.
