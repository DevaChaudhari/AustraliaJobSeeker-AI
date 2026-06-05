# Google Cloud Run Deployment Guide

## Prerequisites
- Google Cloud Project with Cloud Build and Cloud Run enabled
- `gcloud` CLI installed and authenticated
- Docker image pushed to Artifact Registry

## One-Click Deployment (via Cloud Build)

### 1. Enable Required APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 2. Create Artifact Registry Repository
```bash
gcloud artifacts repositories create australiajobseeker-ai \
  --repository-format=docker \
  --location=us-central1 \
  --description="Australia JobSeeker AI - Docker images"
```

### 3. Configure Cloud Build Trigger

#### Option A: GitHub Integration (Recommended)
1. Go to Cloud Build → Triggers → Create Trigger
2. Connect your GitHub repository
3. Configure trigger settings:
   - **Name:** australiajobseeker-ai-deploy
   - **Event:** Push to branch
   - **Branch:** `^main$`
   - **Build configuration:** Cloud Build configuration file
   - **Location:** cloudbuild.yaml

#### Option B: Manual Push
```bash
git push origin main
# Cloud Build will automatically trigger based on cloudbuild.yaml
```

### 4. Set Secrets in Cloud Build

Add your `GROQ_API_KEY` as a Secret:
```bash
gcloud secrets create GROQ_API_KEY --data-file=- <<< "your-groq-api-key"
```

Update `cloudbuild.yaml` to use the secret:
```yaml
steps:
  # ... existing steps ...
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'australiajobseeker-ai'
      - '--image=us-central1-docker.pkg.dev/$PROJECT_ID/australiajobseeker-ai/app:$COMMIT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--port=8080'
      - '--set-env-vars=GROQ_API_KEY=${_GROQ_API_KEY}'
    secretEnv: ['_GROQ_API_KEY']

availableSecrets:
  secretManager:
    - versionName: projects/$PROJECT_ID/secrets/GROQ_API_KEY/versions/latest
      env: '_GROQ_API_KEY'
```

### 5. Deploy to Cloud Run

The `cloudbuild.yaml` will automatically:
1. Build the Docker image
2. Push to Artifact Registry
3. Deploy to Cloud Run
4. Set environment variables

### 6. Monitor Deployment

```bash
# View deployment status
gcloud run services describe australiajobseeker-ai --region=us-central1

# View logs
gcloud run services logs read australiajobseeker-ai --region=us-central1 --limit=50

# Test the deployment
curl https://australiajobseeker-ai-xxxxx.run.app/health
```

## Environment Variables

Cloud Run automatically sets:
- `PORT` (default 8080)
- `PYTHONUNBUFFERED=1`

Add custom variables in Cloud Run service settings or via `cloudbuild.yaml`:
- `GROQ_API_KEY` - Your Groq API key
- `LOG_LEVEL` - Set to DEBUG/INFO/WARNING/ERROR

## Costs & Resource Limits

Configure in Cloud Run:
- **Memory:** 1-8 GB (recommended: 2-4 GB)
- **CPU:** 1-4 (recommended: 1-2)
- **Timeout:** 3600 seconds max
- **Concurrent requests:** Adjust based on needs

```bash
gcloud run services update australiajobseeker-ai \
  --region=us-central1 \
  --memory=2Gi \
  --cpu=2 \
  --timeout=3600
```

## Scaling

Cloud Run automatically scales from 0 to configured max instances:

```bash
gcloud run services update australiajobseeker-ai \
  --region=us-central1 \
  --max-instances=100 \
  --min-instances=0
```

## Troubleshooting

### Build Fails: "file not found"
- Ensure `pyproject.toml` and `uv.lock` exist at root
- Check `.dockerignore` isn't excluding necessary files

### Cloud Run timeout errors
- Increase timeout: `--timeout=3600`
- Check `/health` endpoint responds within 60 seconds

### Memory issues
- Increase memory allocation: `--memory=4Gi`
- Profile with Cloud Profiler

### Cold starts
- Set `--min-instances=1` to keep service warm
- Note: This increases costs

## Rollback to Previous Version

```bash
# Get previous revision
gcloud run revisions list --service=australiajobseeker-ai --region=us-central1

# Route traffic to previous revision
gcloud run services update-traffic australiajobseeker-ai \
  --region=us-central1 \
  --to-revisions REVISION_HASH=100
```

## Clean Up

```bash
# Delete Cloud Run service
gcloud run services delete australiajobseeker-ai --region=us-central1

# Delete Docker image
gcloud artifacts docker images delete \
  us-central1-docker.pkg.dev/$PROJECT_ID/australiajobseeker-ai/app:TAG
```

## Performance Tips

1. **Use Python 3.10 slim image** - Already configured
2. **Cache Docker layers** - Install dependencies in separate layer
3. **Multi-stage builds** - Consider for frontend if needed
4. **Health checks** - Configured in Dockerfile
5. **Request timeouts** - Set appropriately in clients

## CI/CD Pipeline

The complete pipeline is:
1. Code push to `main` branch
2. Cloud Build trigger fires automatically
3. Docker image built with root `Dockerfile`
4. Image pushed to Artifact Registry
5. Cloud Run service deployed with latest image
6. Service automatically scales to handle requests

All in one seamless automated workflow! 🚀
