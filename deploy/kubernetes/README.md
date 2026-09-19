# Australia Job Seeker AI - Kubernetes Deployment Guide ☸️

> Complete guide for deploying AustraliaJobSeeker AI on Kubernetes with production-ready configurations.

![Kubernetes](https://img.shields.io/badge/Kubernetes-1.24%2B-blue) ![Docker](https://img.shields.io/badge/Docker-Ready-brightgreen)

## 📋 Prerequisites

- **Kubernetes Cluster**: minikube, Docker Desktop with K8s, or cloud provider (EKS, GKE, AKS)
- **kubectl**: Installed and configured (v1.24+)
- **Docker Image**: Built locally: `australiajobseeker-ai:latest`
- **Storage**: Persistent Volume support (local-path or cloud provider)
- **(Optional) Ingress Controller**: NGINX Ingress for unified routing

## 🏗️ Architecture Overview

The deployment runs the backend (A2A server, 2 replicas) on ports 9999 and 8000. LLM inference is provided by the Groq API, so `GROQ_API_KEY` must be supplied to the pods.

The backend reads its configuration from a ConfigMap.

## 📄 Configuration Files

| File | Purpose |
|------|---------|
| `namespace.yaml` | Create `australiajobseeker` namespace |
| `configmap.yaml` | Environment variables & API config |
| `pvc.yaml` | Persistent volume for app data (10Gi) |
| `app-deployment.yaml` | Backend: 2 replicas, A2A + FastAPI |
| `app-service.yaml` | Backend service exposure |
| `ingress.yaml` | NGINX Ingress (optional, production) |
| `deploy.sh` | Automated deployment script |

## 🚀 Deployment Steps

### Step 1: Build Docker Image

```bash
# From project root
docker build -t australiajobseeker-ai:latest .

# For minikube: Load image
minikube image load australiajobseeker-ai:latest

# For cloud registries (example: GCR)
docker tag australiajobseeker-ai:latest gcr.io/YOUR-PROJECT/australiajobseeker-ai:latest
docker push gcr.io/YOUR-PROJECT/australiajobseeker-ai:latest
```

### Step 2: Deploy to Kubernetes

```bash
cd deploy/kubernetes/

# Option A: Automated (recommended)
chmod +x deploy.sh && ./deploy.sh

# Option B: Deploy all at once
kubectl apply -f .

# Option C: Step-by-step deployment
kubectl apply -f namespace.yaml && sleep 2
kubectl apply -f configmap.yaml
kubectl apply -f pvc.yaml
kubectl apply -f app-deployment.yaml app-service.yaml
```

### Step 3: Verify Deployment

```bash
# Monitor pods starting (Ctrl+C to exit)
kubectl get pods -n australiajobseeker --watch

# Check all resources
kubectl get all -n australiajobseeker -o wide

# Check pod logs
kubectl logs -n australiajobseeker -l app=app -f
```

## 🌐 Accessing Services

### Local Development (Port Forwarding)

Open separate terminals:

```bash
# Backend API - http://localhost:8000/docs
kubectl port-forward -n australiajobseeker svc/app 8000:8000

# A2A Server - http://localhost:9999
kubectl port-forward -n australiajobseeker svc/app 9999:9999
```

### Cloud LoadBalancer (Production)

```bash
# Get external endpoints
kubectl get svc -n australiajobseeker

# Access using EXTERNAL-IP:PORT
```

### NGINX Ingress

```bash
# Enable on minikube
minikube addons enable ingress

# Deploy ingress
kubectl apply -f ingress.yaml

# Get ingress endpoint
kubectl get ingress -n australiajobseeker
```

## 📊 Monitoring & Management

### Pod Logs

```bash
# Stream app logs
kubectl logs -n australiajobseeker -l app=app -f --tail=100

# Get previous logs (crashed pod)
kubectl logs <POD-NAME> -n australiajobseeker --previous
```

### Pod Operations

```bash
# Shell access for debugging
kubectl exec -it <POD-NAME> -n australiajobseeker -- /bin/bash

# Get pod details
kubectl describe pod <POD-NAME> -n australiajobseeker

# View events
kubectl get events -n australiajobseeker
```

### Resource Monitoring

```bash
# Pod resource usage
kubectl top pods -n australiajobseeker

# Node resource usage
kubectl top nodes
```

## ⚙️ Configuration & Scaling

### Update Environment Variables

```bash
# Edit ConfigMap
kubectl edit configmap app-config -n australiajobseeker

# Apply and restart pods
kubectl rollout restart deployment/app-deployment -n australiajobseeker
```

### Manage Secrets

```bash
# Create API key secret
kubectl create secret generic groq-secret \
  --from-literal=api-key=YOUR-KEY \
  -n australiajobseeker

# Reference in deployment:
# env:
# - name: GROQ_API_KEY
#   valueFrom:
#     secretKeyRef:
#       name: groq-secret
#       key: api-key
```

### Scale Deployments

```bash
# Scale backend
kubectl scale deployment app-deployment \
  --replicas=5 -n australiajobseeker

# Auto-scaling (HPA)
kubectl autoscale deployment app-deployment \
  --min=2 --max=5 --cpu-percent=75 \
  -n australiajobseeker
```

## 🔧 Troubleshooting

### Pod Stuck in Pending

```bash
# Check pod events and resource availability
kubectl describe pod <POD-NAME> -n australiajobseeker
kubectl get nodes
kubectl top nodes
```

### Pod CrashLoopBackOff

```bash
# Check logs for errors
kubectl logs <POD-NAME> -n australiajobseeker --previous
```

### Service Not Accessible

```bash
# Verify service and endpoints exist
kubectl get svc -n australiajobseeker
kubectl get endpoints -n australiajobseeker

# Test DNS and connectivity from pod
kubectl exec -it <POD> -n australiajobseeker -- nslookup app
kubectl exec -it <POD> -n australiajobseeker -- curl http://app:8000/health
```

### Storage Issues

```bash
# Check PVC status
kubectl get pvc -n australiajobseeker
kubectl describe pvc <PVC-NAME> -n australiajobseeker

# Check available storage
kubectl get pv
```

## 📚 Management Operations

```bash
# Update deployment image
kubectl set image deployment/app-deployment \
  app=australiajobseeker-ai:v2 -n australiajobseeker

# Rollback to previous version
kubectl rollout undo deployment/app-deployment -n australiajobseeker

# Restart deployment
kubectl rollout restart deployment/app-deployment -n australiajobseeker

# Backup all resources
kubectl get all -n australiajobseeker -o yaml > backup.yaml

# Delete namespace (deletes all resources)
kubectl delete namespace australiajobseeker
```

## 🔗 Related Documentation

- [Main README](../../README.md)
- [A2A Server](../../docs/a2a-server.md)

---

**Kubernetes deployment guide for AustraliaJobSeeker AI**
