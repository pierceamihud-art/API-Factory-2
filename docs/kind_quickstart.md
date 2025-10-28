# kind Quickstart for API-Factory

Use this guide to validate the Kubernetes manifests locally with [kind](https://kind.sigs.k8s.io/).

## Prerequisites
- Docker running locally
- `kind` CLI installed (`go install sigs.k8s.io/kind@latest` or download release)
- `kubectl` installed (configured automatically by kind)

## Steps
1. **Create a cluster**
   ```bash
   kind create cluster --name api-factory
   ```

2. **Build the Docker image locally**
   ```bash
   docker build -t api-factory:kind .
   ```

3. **Load the image into kind**
   ```bash
   kind load docker-image api-factory:kind --name api-factory
   ```

4. **Apply manifests**
   ```bash
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/hpa.yaml
   ```

5. **Deploy canary (optional)**
   ```bash
   kubectl apply -f k8s/deployment-canary.yaml
   ```

6. **Verify rollout**
   ```bash
   kubectl get pods
   kubectl get hpa
   kubectl logs deployment/api-factory -c api-factory
   ```

7. **Cleanup**
   ```bash
   kind delete cluster --name api-factory
   ```

> Tip: For traffic splitting, configure your ingress or service mesh to direct a small percentage of traffic to pods labeled `track=canary`.
