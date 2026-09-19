#!/usr/bin/env bash
# Build the image, push it to ECR and create/update the CloudFormation stack.
#
# Usage: GROQ_API_KEY=... ./deploy/aws/deploy.sh
# Optional: AWS_REGION (default ap-southeast-2), STACK_NAME, VPC_ID, SUBNET_IDS (comma-separated),
#           ALLOWED_ORIGINS (Amplify URL), BUDGET_EMAIL, CAPACITY_PROVIDER (FARGATE_SPOT|FARGATE)
set -euo pipefail

REGION="${AWS_REGION:-ap-southeast-2}"
STACK="${STACK_NAME:-australiajobseeker-ai}"
: "${GROQ_API_KEY:?Set GROQ_API_KEY}"

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
REPO_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${STACK}"
TAG="$(git rev-parse --short HEAD 2>/dev/null || date +%s)"
IMAGE_URI="${REPO_URI}:${TAG}"

# Default VPC + its subnets unless overridden
VPC_ID="${VPC_ID:-$(aws ec2 describe-vpcs --region "$REGION" --filters Name=isDefault,Values=true \
  --query 'Vpcs[0].VpcId' --output text)}"
SUBNET_IDS="${SUBNET_IDS:-$(aws ec2 describe-subnets --region "$REGION" --filters Name=vpc-id,Values="$VPC_ID" \
  --query 'Subnets[].SubnetId' --output text | tr '\t' ',')}"

CF_PREFIX_LIST="$(aws ec2 describe-managed-prefix-lists --region "$REGION"   --filters Name=prefix-list-name,Values=com.amazonaws.global.cloudfront.origin-facing   --query 'PrefixLists[0].PrefixListId' --output text)"

echo "==> Ensuring ECR repository ${STACK}"
aws ecr describe-repositories --region "$REGION" --repository-names "$STACK" >/dev/null 2>&1 \
  || aws ecr create-repository --region "$REGION" --repository-name "$STACK" >/dev/null

echo "==> Building and pushing ${IMAGE_URI}"
aws ecr get-login-password --region "$REGION" \
  | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
docker build --platform linux/amd64 -t "$IMAGE_URI" .
docker push "$IMAGE_URI"

echo "==> Deploying stack ${STACK}"
aws cloudformation deploy \
  --region "$REGION" \
  --stack-name "$STACK" \
  --template-file "$(dirname "$0")/template.yaml" \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    ImageUri="$IMAGE_URI" \
    VpcId="$VPC_ID" \
    SubnetIds="$SUBNET_IDS" \
    GroqApiKey="$GROQ_API_KEY"     CloudFrontPrefixListId="$CF_PREFIX_LIST"     AllowedOrigins="${ALLOWED_ORIGINS:-*}"     BudgetEmail="${BUDGET_EMAIL:-}"     CapacityProvider="${CAPACITY_PROVIDER:-FARGATE_SPOT}"

aws cloudformation describe-stacks --region "$REGION" --stack-name "$STACK" \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' --output text
