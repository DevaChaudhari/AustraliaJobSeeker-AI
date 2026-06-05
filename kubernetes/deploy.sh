#!/bin/bash
# Australia Job Seeker AI - Kubernetes Deployment Script

set -e

NAMESPACE="australiajobseeker"
IMAGE="australiajobseeker-ai:latest"

echo "🚀 Deploying Australia Job Seeker AI to Kubernetes..."
echo ""

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl."
    exit 1
fi

# Get current context
CONTEXT=$(kubectl config current-context)
echo "📍 Current context: $CONTEXT"
echo ""

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f namespace.yaml

# Create config
echo "⚙️ Creating ConfigMap..."
kubectl apply -f configmap.yaml

# Create PVCs
echo "💾 Creating PersistentVolumeClaims..."
kubectl apply -f pvc.yaml

# Deploy app
echo "🔧 Deploying backend (A2A)..."
kubectl apply -f app-deployment.yaml
kubectl apply -f app-service.yaml

# Deploy frontend
echo "🎨 Deploying frontend (Streamlit)..."
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml

# Deploy Ollama
echo "🦙 Deploying Ollama..."
kubectl apply -f ollama-deployment.yaml
kubectl apply -f ollama-service.yaml

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Checking status..."
kubectl get all -n $NAMESPACE

echo ""
echo "🌐 Service endpoints:"
kubectl get svc -n $NAMESPACE

echo ""
echo "⏳ Waiting for pods to be ready (this may take a minute)..."
kubectl rollout status deployment/app -n $NAMESPACE --timeout=5m
kubectl rollout status deployment/frontend -n $NAMESPACE --timeout=5m
kubectl rollout status deployment/ollama -n $NAMESPACE --timeout=5m

echo ""
echo "✨ All services deployed successfully!"
echo ""
echo "📝 Next steps:"
echo "  1. Port forward to access locally:"
echo "     kubectl port-forward -n $NAMESPACE svc/frontend 8501:8501"
echo "  2. Visit: http://localhost:8501"
echo ""
echo "💡 View logs:"
echo "   kubectl logs -n $NAMESPACE -l app=australiajobseeker-frontend -f"
echo "   kubectl logs -n $NAMESPACE -l app=australiajobseeker-app -f"
echo "   kubectl logs -n $NAMESPACE -l app=ollama -f"
echo ""
echo "🗑️  To cleanup:"
echo "   kubectl delete namespace $NAMESPACE"
