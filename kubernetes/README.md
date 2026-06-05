# Australia Job Seeker AI - Kubernetes Deployment Guide

## Prerequisites
- Kubernetes cluster running (minikube, Docker Desktop with K8s, or cloud provider)
- kubectl installed and configured
- Docker image built and available: `australiajobseeker-ai:latest`
- (Optional) NGINX Ingress Controller for Ingress routing

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Frontend (Streamlit - Port 8501)                            │
│ - Resume upload & job search UI                             │
│ - Talks to Backend API at http://app:8000                   │
└─────────────────┬───────────────────────────────────────────┘
                  │ (BACKEND_URL=http://app:8000)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ App (A2A Server - Ports 9999/8000)                          │
│ - Port 9999: A2A API                                        │
│ - Port 8000: Backend API (search, resume, cover letter)     │
│ - Connects to Ollama at http://ollama:11434                 │
└─────────────────┬───────────────────────────────────────────┘
                  │ (OLLAMA_HOST=http://ollama:11434)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Ollama (Language Model Server - Port 11434)                 │
│ - Serves LLM inference for AI features                      │
└─────────────────────────────────────────────────────────────┘
```

## Files Overview

- **namespace.yaml** — Creates isolated namespace `australiajobseeker`
- **configmap.yaml** — Environment config (OLLAMA_HOST, LOG_LEVEL)
- **pvc.yaml** — Persistent storage for app data (10Gi) and Ollama models (20Gi)
- **app-deployment.yaml** — A2A backend (2 replicas, command: `python -m A2A.main`)
- **app-service.yaml** — LoadBalancer + ClusterIP services for backend
- **frontend-deployment.yaml** — Streamlit frontend (2 replicas, command: `streamlit run frontend/app.py`)
- **frontend-service.yaml** — LoadBalancer service for frontend (port 8501)
- **ollama-deployment.yaml** — Ollama server (1 replica, persistent volume)
- **ollama-service.yaml** — ClusterIP + LoadBalancer services for Ollama
- **ingress.yaml** — (Optional) NGINX Ingress for unified routing

## Deployment Steps

### 1. Prepare Docker Image

**If using minikube:**
```bash
# Build locally and load into minikube
docker build -t australiajobseeker-ai:latest ..
minikube image load australiajobseeker-ai:latest
```

**If using Docker Desktop with K8s:**
```bash
# Build locally (automatically available)
docker build -t australiajobseeker-ai:latest ..
```

### 2. Deploy All Resources

```bash
cd F:\AustraliaJobSeeker-AI\Kubernetes

# Deploy all manifests at once
kubectl apply -f .

# OR deploy step-by-step
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f pvc.yaml
kubectl apply -f app-deployment.yaml
kubectl apply -f app-service.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
kubectl apply -f ollama-deployment.yaml
kubectl apply -f ollama-service.yaml
# kubectl apply -f ingress.yaml  # Only if NGINX Ingress is installed
```

### 3. Verify Deployment

```bash
# Check namespace
kubectl get namespace

# Check all resources
kubectl get all -n australiajobseeker

# Check pods
kubectl get pods -n australiajobseeker
kubectl get pods -n australiajobseeker --watch

# Check services
kubectl get svc -n australiajobseeker

# Check persistent volumes
kubectl get pvc -n australiajobseeker

# Check pod logs
kubectl logs -n australiajobseeker -l app=australiajobseeker-frontend --tail=50 -f
kubectl logs -n australiajobseeker -l app=australiajobseeker-app --tail=50 -f
kubectl logs -n australiajobseeker -l app=ollama --tail=50 -f
```

### 4. Access Your Application

**Using LoadBalancer (if available):**
```bash
# Get external IPs
kubectl get svc -n australiajobseeker

# Frontend: http://<FRONTEND_EXTERNAL_IP>:8501
# A2A API: http://<APP_EXTERNAL_IP>:9999
# Backend API: http://<APP_EXTERNAL_IP>:8000
# Ollama: http://<OLLAMA_EXTERNAL_IP>:11434
```

**Using Port Forwarding (local testing):**
```bash
# Terminal 1 - Frontend
kubectl port-forward -n australiajobseeker svc/frontend 8501:8501

# Terminal 2 - Backend API
kubectl port-forward -n australiajobseeker svc/app 8000:8000

# Terminal 3 - A2A API
kubectl port-forward -n australiajobseeker svc/app 9999:9999

# Terminal 4 - Ollama
kubectl port-forward -n australiajobseeker svc/ollama 11434:11434

# Then access at:
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000
# A2A API: http://localhost:9999
# Ollama: http://localhost:11434
```

**Using Ingress (if installed):**
```bash
# Install NGINX Ingress Controller (if not already installed)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx

# Access single endpoint
# Frontend: http://localhost/
# Backend API: http://localhost/api
# A2A API: http://localhost/a2a
# Ollama: http://localhost/ollama
```

### 5. Common Operations

```bash
# Scale frontend to 3 replicas
kubectl scale deployment frontend -n australiajobseeker --replicas=3

# Scale app to 4 replicas
kubectl scale deployment app -n australiajobseeker --replicas=4

# View real-time resource usage
kubectl top nodes
kubectl top pods -n australiajobseeker

# Restart a pod
kubectl delete pod <pod-name> -n australiajobseeker

# View pod details
kubectl describe pod <pod-name> -n australiajobseeker

# Exec into a pod (debugging)
kubectl exec -it <pod-name> -n australiajobseeker -- /bin/bash

# Check events
kubectl get events -n australiajobseeker
```

### 6. Update Deployment

```bash
# Update image
kubectl set image deployment/app app=australiajobseeker-ai:v2 -n australiajobseeker
kubectl set image deployment/frontend frontend=australiajobseeker-ai:v2 -n australiajobseeker

# Rollback
kubectl rollout undo deployment/app -n australiajobseeker
kubectl rollout undo deployment/frontend -n australiajobseeker

# Check rollout status
kubectl rollout status deployment/app -n australiajobseeker
```

### 7. Delete Deployment

```bash
# Delete entire namespace (deletes all resources)
kubectl delete namespace australiajobseeker

# OR delete specific resources
kubectl delete -f .
```

## Resource Requests & Limits

**Frontend Pod:**
- CPU Request: 100m | Limit: 250m
- Memory Request: 256Mi | Limit: 512Mi

**App Pod:**
- CPU Request: 250m | Limit: 500m
- Memory Request: 512Mi | Limit: 1Gi

**Ollama Pod:**
- CPU Request: 1000m | Limit: 2000m
- Memory Request: 2Gi | Limit: 4Gi

Adjust in deployment manifests based on cluster capacity.

## Troubleshooting

### Pods Stuck in Pending
```bash
kubectl describe pod <pod-name> -n australiajobseeker
# Check: PVC not bound, insufficient resources, image pull errors
```

### Pod Crashes (CrashLoopBackOff)
```bash
kubectl logs <pod-name> -n australiajobseeker
# Common: missing dependencies, bad environment variables, port conflicts
```

### High Memory Usage
```bash
kubectl top pods -n australiajobseeker --sort-by=memory
# Increase `limits.memory` in deployment manifests
```

### Connection Errors Between Services
```bash
# Verify service DNS is working
kubectl exec -it <pod-name> -n australiajobseeker -- nslookup app
kubectl exec -it <pod-name> -n australiajobseeker -- nslookup ollama

# Check network policies
kubectl get networkpolicies -n australiajobseeker
```

## Production Considerations

- Use **Horizontal Pod Autoscaler (HPA)** for auto-scaling based on CPU/memory
- Enable **Resource Quotas** to limit namespace resource consumption
- Use **Network Policies** to restrict traffic between pods
- Implement **Liveness and Readiness Probes** (already included)
- Use **ConfigMaps** and **Secrets** for configuration management
- Enable **Persistent Volumes** for data durability
- Set up **Ingress** with TLS certificates for HTTPS
- Use **StatefulSets** for stateful components if needed
- Enable **Pod Disruption Budgets** for high availability
- Monitor with **Prometheus + Grafana** or similar
