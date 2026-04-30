# Smoke test jobs

Each manifest in this folder runs one smoke/stress scenario in an isolated pod.

Expected image content:
- project source code
- Python runtime
- dependencies from `requirements.txt`

Build the test image from the shared root Dockerfile:

```powershell
docker build -t swiip23/blurmoji .
```

Default namespace in examples: `blurmoji`.

Apply all jobs:

```powershell
kubectl apply -f src/deploy/k8s/tests/configmap.yaml
kubectl apply -f src/deploy/k8s/tests/job-queue-delay.yaml
kubectl apply -f src/deploy/k8s/tests/job-concurrent-sessions.yaml
kubectl apply -f src/deploy/k8s/tests/job-gateway-restrictions.yaml
kubectl apply -f src/deploy/k8s/tests/job-stress.yaml
kubectl apply -f src/deploy/k8s/tests/job-connectivity.yaml
```
