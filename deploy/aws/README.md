# Deploying to AWS

```
Browser ──> Amplify Hosting (React app in frontend/)
   │
   └──HTTPS──> CloudFront ──HTTP──> ALB ──> ECS Fargate (FastAPI + Playwright)
```

The backend and frontend are deployed separately. Deploy the backend first, because the
frontend needs its URL.

## 1. Prerequisites

- AWS CLI v2, configured with `aws configure` (check with `aws sts get-caller-identity`)
- Docker running
- A Groq API key
- Git Bash or WSL to run the script

## 2. Deploy the backend

```bash
GROQ_API_KEY=your_key BUDGET_EMAIL=you@example.com ./deploy/aws/deploy.sh
```

This creates the ECR repo, builds and pushes the image, then deploys `template.yaml`.
The first run takes ~10 minutes. It prints the **ApiUrl** (an `https://xxxx.cloudfront.net` URL).

Check it: `curl <ApiUrl>/health`

Options (environment variables): `AWS_REGION` (default `ap-southeast-2`), `STACK_NAME`,
`CAPACITY_PROVIDER` (`FARGATE_SPOT` default, or `FARGATE`), `ALLOWED_ORIGINS`, `BUDGET_EMAIL`.

## 3. Deploy the frontend on Amplify

1. Push this repo to GitHub (Amplify builds from it).
2. AWS Console > **AWS Amplify** > **Create new app** > **GitHub** > pick the repo and `main` branch.
3. Amplify detects the monorepo config in [`amplify.yml`](../../amplify.yml) (app root `frontend/`).
4. Under **Environment variables**, add `VITE_API_URL` = the **ApiUrl** from step 2 (no trailing slash).
5. Save and deploy. Amplify gives you a URL like `https://main.xxxx.amplifyapp.com`.

## 4. Lock down CORS

The backend allows any origin until you restrict it. Redeploy with your Amplify URL:

```bash
ALLOWED_ORIGINS=https://main.xxxx.amplifyapp.com GROQ_API_KEY=your_key ./deploy/aws/deploy.sh
```

## Notes

- **Timeouts:** CloudFront waits at most 60s for the backend. The frontend uses
  `POST /search-jobs/async` and polls `GET /search-jobs/{id}`, so long searches are fine.
  Search state is kept in memory, so keep `DesiredCount` at 1. A Spot interruption loses
  in-flight searches; the user just searches again.
- **Direct ALB access is blocked:** the load balancer only accepts traffic from CloudFront.
- **Changing the backend URL:** if you delete and redeploy the stack, the CloudFront URL changes.
  Update `VITE_API_URL` in Amplify and trigger a redeploy.

## Cost and shutting down

Running cost is roughly $25-35/month with Fargate Spot, or $65-80 on regular Fargate. It is a fixed
cost: it does not depend on traffic. Amplify is about $0-2/month.

| Goal | Command |
|---|---|
| Stop all backend charges | `aws cloudformation delete-stack --region ap-southeast-2 --stack-name australiajobseeker-ai` |
| Remove the image repo | `aws ecr delete-repository --region ap-southeast-2 --repository-name australiajobseeker-ai --force` |
| Bring it back | run `./deploy/aws/deploy.sh` again, then update `VITE_API_URL` in Amplify |

Setting `DesiredCount=0` pauses the task but the load balancer keeps billing, so deleting the stack is the way to
stop charges.
