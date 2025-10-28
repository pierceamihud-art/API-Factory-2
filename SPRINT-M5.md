# Sprint M5: Canary / Rollout & Scaling

Goal: prepare artifacts and automation for safe rollout and scaling of the API service.

Primary deliverables
- Container image publishing pipeline (CI) with tags for `canary` and `stable`.
- Kubernetes manifests (Deployment, Service, HPA) and a simple canary rollout strategy.
- CI job to build and push images, optionally to GitHub Container Registry or Docker Hub.
- Load testing plan and smoke tests for canary.
- Scaling and resource guidance (CPU/memory requests & limits, HPA target metrics).

Order of work (small PRs)
1. CI: add `build-and-publish` workflow (or extend existing `ci.yml`) that builds Docker image and optionally pushes to registry (feature-flag via env). Include cache for pip and Docker layers.
2. Manifests: add `k8s/` folder with `deployment.yaml`, `service.yaml`, `hpa.yaml`, and a `kustomization.yaml` for overlays (dev/canary/prod).
3. Canary strategy: provide a simple script or manifest set that deploys `canary` label with reduced replicas and a traffic split (manual or via ingress/Service mesh doc). Document roll-forward/rollback steps.
4. Load testing: add a lightweight `locustfile.py` or JMeter script and a `Makefile` target to run a local smoke test against a canary.
5. Add docs: `docs/canary.md` with exact steps for deploy, test, and rollback.

Immediate next step (what I'll do now)
- Run the CI lint job locally (install `ruff` and run `ruff check .`) to mirror CI lint.

Acceptance criteria
- `ruff check .` passes in local run (CI lint job passes).
- `k8s/` manifests added (PR-ready) with clara instructions.
- CI has a build step that can be toggled to push images to a registry.

Notes
- We'll avoid publishing credentials to the repo. CI uses repo secrets to push images.
- For cluster testing, a staging k8s cluster or kind can be used; we'll document how to use `kind` for local canary testing.
