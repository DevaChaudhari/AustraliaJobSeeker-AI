#!/usr/bin/env bash
# Build the Lambda image, push it to ECR and create/update the CloudFormation stack.
#
# Usage: GROQ_API_KEY=... ./deploy/aws/deploy.sh
# Optional: AWS_REGION (default ap-southeast-2), STACK_NAME, IMAGE_TAG (default: git short hash),
#           ALLOWED_ORIGINS (frontend URL), MEMORY_SIZE (MB, default 2048),
#           BUDGET_EMAIL, BUDGET_LIMIT_USD (default 5)
set -euo pipefail

REGION="${AWS_REGION:-ap-southeast-2}"
STACK="${STACK_NAME:-australiajobseeker-ai}"
: "${GROQ_API_KEY:?Set GROQ_API_KEY}"

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
REGISTRY="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
TAG="${IMAGE_TAG:-$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || date +%s)}"
# A unique tag per build so Lambda always picks up the new image
TAG="${TAG}-$(date +%Y%m%d%H%M%S)"
IMAGE_URI="${REGISTRY}/${STACK}:${TAG}"

echo "==> Ensuring ECR repository ${STACK}"
if ! aws ecr describe-repositories --region "$REGION" --repository-names "$STACK" >/dev/null 2>&1; then
  aws ecr create-repository --region "$REGION" --repository-name "$STACK" >/dev/null
fi
# Keep only the 2 newest images so storage stays around 3 GB at most (about $0.10 per GB-month)
aws ecr put-lifecycle-policy --region "$REGION" --repository-name "$STACK" --lifecycle-policy-text \
  '{"rules":[{"rulePriority":1,"description":"keep 2 newest","selection":{"tagStatus":"any","countType":"imageCountMoreThan","countNumber":2},"action":{"type":"expire"}}]}' \
  >/dev/null

echo "==> Building and pushing ${IMAGE_URI}"
aws ecr get-login-password --region "$REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"
# Lambda rejects multi-platform manifests, so build one plain amd64 image without provenance
docker build --platform linux/amd64 --provenance=false -f "$ROOT/Dockerfile.lambda" -t "$IMAGE_URI" "$ROOT"
docker push "$IMAGE_URI"

echo "==> Deploying stack ${STACK}"
aws cloudformation deploy \
  --region "$REGION" \
  --stack-name "$STACK" \
  --template-file "$ROOT/deploy/aws/template.yaml" \
  --capabilities CAPABILITY_IAM \
  --no-fail-on-empty-changeset \
  --parameter-overrides \
    ImageUri="$IMAGE_URI" \
    GroqApiKey="$GROQ_API_KEY" \
    AllowedOrigins="${ALLOWED_ORIGINS:-*}" \
    MemorySize="${MEMORY_SIZE:-2048}" \
    BudgetEmail="${BUDGET_EMAIL:-}" \
    BudgetLimitUsd="${BUDGET_LIMIT_USD:-5}"

API_URL="$(aws cloudformation describe-stacks --region "$REGION" --stack-name "$STACK" \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' --output text)"
echo
echo "API URL (use as VITE_API_URL): ${API_URL%/}"
echo "Check it: curl ${API_URL%/}/health"
