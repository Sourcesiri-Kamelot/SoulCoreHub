#!/bin/bash
# SoulCoreHub AWS Services Setup Script
# This script sets up various AWS services for SoulCoreHub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-dev}
REGION=${2:-us-east-1}
STACK_PREFIX="soulcorehub"

# Print header
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  SoulCoreHub AWS Services Setup  ${NC}"
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

# Function to create and configure an AWS service
create_service() {
    service_name=$1
    service_type=$2
    echo -e "${YELLOW}Setting up ${service_name}...${NC}"
    
    case $service_type in
        "s3")
            bucket_name="${STACK_PREFIX}-${service_name}-${ENVIRONMENT}"
            if ! aws s3api head-bucket --bucket "$bucket_name" 2>/dev/null; then
                aws s3 mb "s3://${bucket_name}" --region "$REGION"
                aws s3api put-bucket-encryption \
                    --bucket "$bucket_name" \
                    --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
                aws s3api put-bucket-versioning --bucket "$bucket_name" --versioning-configuration Status=Enabled
                echo -e "${GREEN}Created S3 bucket: ${bucket_name}${NC}"
            else
                echo -e "${YELLOW}S3 bucket already exists: ${bucket_name}${NC}"
            fi
            ;;
            
        "dynamodb")
            table_name="${STACK_PREFIX}-${service_name}-${ENVIRONMENT}"
            if ! aws dynamodb describe-table --table-name "$table_name" 2>/dev/null; then
                aws dynamodb create-table \
                    --table-name "$table_name" \
                    --attribute-definitions AttributeName=id,AttributeType=S \
                    --key-schema AttributeName=id,KeyType=HASH \
                    --billing-mode PAY_PER_REQUEST \
                    --region "$REGION"
                echo -e "${GREEN}Created DynamoDB table: ${table_name}${NC}"
            else
                echo -e "${YELLOW}DynamoDB table already exists: ${table_name}${NC}"
            fi
            ;;
            
        "lambda")
            function_name="${STACK_PREFIX}-${service_name}-${ENVIRONMENT}"
            if ! aws lambda get-function --function-name "$function_name" 2>/dev/null; then
                # Create a temporary deployment package
                echo "exports.handler = async (event) => { return { statusCode: 200, body: 'Function created' }; };" > /tmp/index.js
                zip -j /tmp/function.zip /tmp/index.js
                
                # Create execution role
                role_name="${function_name}-role"
                trust_policy='{
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }]
                }'
                
                # Check if role exists
                if ! aws iam get-role --role-name "$role_name" 2>/dev/null; then
                    aws iam create-role --role-name "$role_name" --assume-role-policy-document "$trust_policy"
                    aws iam attach-role-policy --role-name "$role_name" --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
                    # Wait for role to propagate
                    echo -e "${YELLOW}Waiting for IAM role to propagate...${NC}"
                    sleep 10
                fi
                
                # Get role ARN
                role_arn=$(aws iam get-role --role-name "$role_name" --query "Role.Arn" --output text)
                
                # Create Lambda function
                aws lambda create-function \
                    --function-name "$function_name" \
                    --runtime nodejs18.x \
                    --handler index.handler \
                    --role "$role_arn" \
                    --zip-file fileb:///tmp/function.zip \
                    --region "$REGION"
                
                echo -e "${GREEN}Created Lambda function: ${function_name}${NC}"
                
                # Clean up
                rm /tmp/index.js /tmp/function.zip
            else
                echo -e "${YELLOW}Lambda function already exists: ${function_name}${NC}"
            fi
            ;;
            
        "sns")
            topic_name="${STACK_PREFIX}-${service_name}-${ENVIRONMENT}"
            topic_arn=$(aws sns create-topic --name "$topic_name" --region "$REGION" --query "TopicArn" --output text)
            echo -e "${GREEN}Created or retrieved SNS topic: ${topic_name} (${topic_arn})${NC}"
            ;;
            
        "sqs")
            queue_name="${STACK_PREFIX}-${service_name}-${ENVIRONMENT}"
            queue_url=$(aws sqs create-queue --queue-name "$queue_name" --region "$REGION" --query "QueueUrl" --output text)
            echo -e "${GREEN}Created or retrieved SQS queue: ${queue_name} (${queue_url})${NC}"
            ;;
            
        "cognito")
            pool_name="${STACK_PREFIX}-${service_name}-${ENVIRONMENT}"
            if ! aws cognito-idp list-user-pools --max-results 60 --region "$REGION" --query "UserPools[?Name=='$pool_name'].Id" --output text | grep -q .; then
                pool_id=$(aws cognito-idp create-user-pool --pool-name "$pool_name" --region "$REGION" --query "UserPool.Id" --output text)
                
                # Create app client
                client_id=$(aws cognito-idp create-user-pool-client \
                    --user-pool-id "$pool_id" \
                    --client-name "${pool_name}-client" \
                    --no-generate-secret \
                    --region "$REGION" \
                    --query "UserPoolClient.ClientId" \
                    --output text)
                
                echo -e "${GREEN}Created Cognito user pool: ${pool_name} (${pool_id}) with client ${client_id}${NC}"
            else
                pool_id=$(aws cognito-idp list-user-pools --max-results 60 --region "$REGION" --query "UserPools[?Name=='$pool_name'].Id" --output text)
                echo -e "${YELLOW}Cognito user pool already exists: ${pool_name} (${pool_id})${NC}"
            fi
            ;;
            
        "cloudfront")
            distribution_name="${STACK_PREFIX}-${service_name}-${ENVIRONMENT}"
            bucket_name="${STACK_PREFIX}-${service_name}-${ENVIRONMENT}"
            
            # Create S3 bucket if it doesn't exist
            if ! aws s3api head-bucket --bucket "$bucket_name" 2>/dev/null; then
                aws s3 mb "s3://${bucket_name}" --region "$REGION"
                aws s3api put-bucket-policy --bucket "$bucket_name" --policy '{
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "cloudfront.amazonaws.com"
                            },
                            "Action": "s3:GetObject",
                            "Resource": "arn:aws:s3:::'$bucket_name'/*"
                        }
                    ]
                }'
                echo -e "${GREEN}Created S3 bucket for CloudFront: ${bucket_name}${NC}"
            fi
            
            # Create CloudFront distribution
            # This is a simplified version, in practice you'd use CloudFormation for this
            echo -e "${YELLOW}For CloudFront distribution, please use the AWS Console or CloudFormation.${NC}"
            echo -e "${YELLOW}A basic distribution would use the S3 bucket ${bucket_name} as its origin.${NC}"
            ;;
            
        "eventbridge")
            rule_name="${STACK_PREFIX}-${service_name}-${ENVIRONMENT}"
            if ! aws events describe-rule --name "$rule_name" --region "$REGION" 2>/dev/null; then
                aws events put-rule \
                    --name "$rule_name" \
                    --schedule-expression "rate(1 day)" \
                    --state ENABLED \
                    --region "$REGION"
                echo -e "${GREEN}Created EventBridge rule: ${rule_name}${NC}"
            else
                echo -e "${YELLOW}EventBridge rule already exists: ${rule_name}${NC}"
            fi
            ;;
            
        *)
            echo -e "${RED}Unknown service type: ${service_type}${NC}"
            ;;
    esac
}

# Setup core services
create_service "data" "s3"
create_service "logs" "s3"
create_service "state" "dynamodb"
create_service "users" "dynamodb"
create_service "content" "dynamodb"
create_service "processor" "lambda"
create_service "notifications" "sns"
create_service "tasks" "sqs"
create_service "auth" "cognito"
create_service "cdn" "cloudfront"
create_service "scheduler" "eventbridge"

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  AWS Services Setup Complete!  ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "${YELLOW}The following services have been set up:${NC}"
echo -e "- S3 buckets for data and logs"
echo -e "- DynamoDB tables for state, users, and content"
echo -e "- Lambda function for processing"
echo -e "- SNS topic for notifications"
echo -e "- SQS queue for tasks"
echo -e "- Cognito user pool for authentication"
echo -e "- CloudFront distribution setup instructions"
echo -e "- EventBridge rule for scheduling"
echo -e ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Update your .env file with the created resource names/ARNs"
echo -e "2. Deploy your application code to the Lambda function"
echo -e "3. Configure the EventBridge rule with appropriate targets"
echo -e ""
