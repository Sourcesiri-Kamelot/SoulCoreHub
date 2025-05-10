#!/bin/bash
# SoulCoreHub Infrastructure Deployment Script
# This script deploys the CloudFormation stacks for SoulCoreHub

set -e

# Configuration
ENVIRONMENT=${1:-dev}
REGION=${2:-us-east-1}
STACK_PREFIX="soulcorehub"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  SoulCoreHub Infrastructure Deployment  ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "${YELLOW}Environment: ${ENVIRONMENT}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}AWS credentials are not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

# Create S3 bucket for CloudFormation templates if it doesn't exist
BUCKET_NAME="${STACK_PREFIX}-cfn-templates-${ENVIRONMENT}"
if ! aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
    echo -e "${YELLOW}Creating S3 bucket for CloudFormation templates...${NC}"
    aws s3 mb "s3://${BUCKET_NAME}" --region "$REGION"
    aws s3api put-bucket-versioning --bucket "$BUCKET_NAME" --versioning-configuration Status=Enabled
    echo -e "${GREEN}S3 bucket created.${NC}"
else
    echo -e "${YELLOW}S3 bucket already exists.${NC}"
fi

# Upload CloudFormation templates to S3
echo -e "${YELLOW}Uploading CloudFormation templates to S3...${NC}"
aws s3 sync infrastructure/cloudformation/ "s3://${BUCKET_NAME}/templates/" --delete

# Deploy base infrastructure stack
BASE_STACK_NAME="${STACK_PREFIX}-base-${ENVIRONMENT}"
echo -e "${YELLOW}Deploying base infrastructure stack...${NC}"
aws cloudformation deploy \
    --template-file infrastructure/cloudformation/base_infrastructure.yaml \
    --stack-name "$BASE_STACK_NAME" \
    --parameter-overrides \
        Environment="$ENVIRONMENT" \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --region "$REGION"

# Deploy API Gateway stack
API_STACK_NAME="${STACK_PREFIX}-api-${ENVIRONMENT}"
echo -e "${YELLOW}Deploying API Gateway stack...${NC}"
aws cloudformation deploy \
    --template-file infrastructure/cloudformation/api_gateway_stack.yaml \
    --stack-name "$API_STACK_NAME" \
    --parameter-overrides \
        Environment="$ENVIRONMENT" \
    --capabilities CAPABILITY_IAM \
    --region "$REGION"

# Deploy agent stacks
for AGENT in "GPTSoul" "Anima" "EvoVe" "Azur"; do
    AGENT_STACK_NAME="${STACK_PREFIX}-${AGENT,,}-${ENVIRONMENT}"
    echo -e "${YELLOW}Deploying ${AGENT} agent stack...${NC}"
    aws cloudformation deploy \
        --template-file infrastructure/cloudformation/agent_base_stack.yaml \
        --stack-name "$AGENT_STACK_NAME" \
        --parameter-overrides \
            Environment="$ENVIRONMENT" \
            AgentName="$AGENT" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --region "$REGION"
done

# Get API Gateway URL
API_URL=$(aws cloudformation describe-stacks --stack-name "$API_STACK_NAME" --query "Stacks[0].Outputs[?OutputKey=='ApiGatewayUrl'].OutputValue" --output text --region "$REGION")

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Deployment Complete!  ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "${YELLOW}API Gateway URL: ${API_URL}${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Deploy agent code using the CI/CD pipeline"
echo -e "2. Configure DNS for the API Gateway"
echo -e "3. Set up monitoring and alerting"
echo ""
