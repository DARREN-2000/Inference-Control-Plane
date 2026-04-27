# Kubernetes Deployment

This directory provides a baseline Kubernetes deployment for the control plane.

## Layout

- `base/`: core manifests for app, postgres, redis, and prometheus

## Usage

Apply all base manifests:

```bash
kubectl apply -f deploy/kubernetes/base
```

## Important Notes

- Replace values in `secret.example.yaml` with real secrets before deployment.
- For production, prefer managed PostgreSQL and Redis services.
- Use an Ingress or API gateway in front of `inference-control-plane` service.
