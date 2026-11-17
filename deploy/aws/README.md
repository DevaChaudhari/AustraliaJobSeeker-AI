# Deploying to AWS

```
Browser ──> Amplify Hosting (React app in frontend/)
   │
   └──HTTPS──> Lambda Function URL ──> Lambda (FastAPI + Playwright, container image)
```

The backend is a single Lambda function. It runs only when someone uses the app, so an idle demo
costs nothing: no load balancer, no CloudFront, no always-on container.

Deploy the backend first, because the frontend needs its URL.

## 1. Prerequisites

- AWS CLI, configured with `aws configure` (check with `aws sts get-caller-identity`)
- Docker running
- A Groq API key
- Git Bash or WSL to run the script

## 2. Deploy the backend

```bash
GROQ_API_KEY=your_key BUDGET_EMAIL=you@example.com ./deploy/aws/deploy.sh
```

This creates the ECR repo, builds [`Dockerfile.lambda`](../../Dockerfile.lambda), pushes it, then
deploys [`template.yaml`](template.yaml). The first run takes about 10 minutes (mostly the image
build and upload). It prints the **API URL**, like `https://xxxx.lambda-url.ap-southeast-2.on.aws`.

Check it: `curl <API URL>/health`. The first call after a quiet period takes 5-15 seconds while
Lambda starts the container.

Options (environment variables): `AWS_REGION` (default `ap-southeast-2`), `STACK_NAME`,
`ALLOWED_ORIGINS`, `MEMORY_SIZE` (default 2048), `BUDGET_EMAIL`, `BUDGET_LIMIT_USD` (default 5).

## 3. Frontend on Amplify, deployed by GitHub Actions

The live site is **https://main.d1ffqg8xlvl7zp.amplifyapp.com** (Amplify app `d1ffqg8xlvl7zp`).

Every push to `main` that changes `frontend/` runs
[`.github/workflows/deploy-frontend.yml`](../../.github/workflows/deploy-frontend.yml). It builds the
app with `VITE_API_URL` set and uploads it to that same Amplify app, so the URL never changes.
To redeploy without a code change: GitHub > **Actions** > **Deploy frontend to Amplify** > **Run workflow**.

GitHub signs in to AWS through a short-lived OIDC role from [`github-oidc.yaml`](github-oidc.yaml).
No AWS keys are stored in GitHub, and the role can only deploy this one Amplify app from `main`.
It was created once with:

```bash
aws cloudformation deploy --region ap-southeast-2 --stack-name australiajobseeker-ai-github \
  --template-file deploy/aws/github-oidc.yaml --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides AmplifyAppId=d1ffqg8xlvl7zp
```

Do not delete the Amplify app: a new app gets a new random URL, and a deleted app's URL cannot be reused.
If the backend API URL changes, update `VITE_API_URL` in the workflow file.

## 4. Lock down CORS

The backend allows any origin until you restrict it. Redeploy with your frontend URL:

```bash
ALLOWED_ORIGINS=https://main.d1ffqg8xlvl7zp.amplifyapp.com GROQ_API_KEY=your_key ./deploy/aws/deploy.sh
```

Always pass `ALLOWED_ORIGINS` when redeploying the backend, or it goes back to allowing any origin.

## Notes

- **Searches are one request.** The frontend calls `POST /search-jobs` and waits. A Function URL can
  wait up to 15 minutes, and Lambda keeps nothing in memory between calls, so the async
  start-then-poll endpoints do not work here (they still work when running locally or in Docker).
- **The API URL is stable.** Redeploying updates the same function and keeps the URL. It only
  changes if you delete the stack.

## Cost and shutting down

| Item | Per month for a demo |
|---|---|
| Lambda (2 GB, about 1 minute per search) | $0. The always-free allowance covers about 3,000 searches |
| Function URL | $0 |
| ECR image storage (about 1.5 GB, 2 newest images kept) | about $0.15-0.30 |
| CloudWatch Logs (7 days) | about $0 |
| Amplify frontend | about $0 |

| Goal | Command |
|---|---|
| Remove the backend | `aws cloudformation delete-stack --region ap-southeast-2 --stack-name australiajobseeker-ai` |
| Remove the image repo | `aws ecr delete-repository --region ap-southeast-2 --repository-name australiajobseeker-ai --force` |
| Bring it back | run `./deploy/aws/deploy.sh` again, then update `VITE_API_URL` in Amplify |
