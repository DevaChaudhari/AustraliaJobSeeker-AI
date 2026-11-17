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

## 3. Deploy the frontend on Amplify

1. Push this repo to GitHub (Amplify builds from it).
2. AWS Console > **AWS Amplify** > **Create new app** > **GitHub** > pick the repo and `main` branch.
3. Amplify detects the monorepo config in [`amplify.yml`](../../amplify.yml) (app root `frontend/`).
4. Under **Environment variables**, add `VITE_API_URL` = the **API URL** from step 2 (no trailing slash).
5. Save and deploy. Amplify gives you a URL like `https://main.xxxx.amplifyapp.com`.

Each new Amplify app gets a new random `xxxx`. A deleted app's URL cannot be reused.

## 4. Lock down CORS

The backend allows any origin until you restrict it. Redeploy with your frontend URL:

```bash
ALLOWED_ORIGINS=https://main.xxxx.amplifyapp.com GROQ_API_KEY=your_key ./deploy/aws/deploy.sh
```

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
