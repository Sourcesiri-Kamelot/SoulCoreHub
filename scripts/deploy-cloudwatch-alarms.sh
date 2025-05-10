#!/bin/bash

# SoulCoreHub CloudWatch Alarms Deployment Script
# This script deploys CloudWatch alarms for monitoring SoulCoreHub

echo "🔔 SoulCoreHub CloudWatch Alarms Deployment"
echo "========================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Get parameters
STAGE=${1:-evolve}
EMAIL=${2:-alerts@soulcorehub.io}

# Get the API name and Lambda function prefix from CloudFormation
API_NAME=$(aws cloudformation describe-stacks --stack-name soulcore-anima --query "Stacks[0].Outputs[?OutputKey=='SoulCoreApi'].OutputValue" --output text | cut -d'/' -f3)
LAMBDA_PREFIX="soulcore-anima"

echo "📊 Deploying CloudWatch alarms for SoulCoreHub"
echo "  Stage: $STAGE"
echo "  API Name: $API_NAME"
echo "  Lambda Function Prefix: $LAMBDA_PREFIX"
echo "  Notification Email: $EMAIL"

# Deploy the CloudWatch alarms
aws cloudformation deploy \
  --template-file cloudwatch-alarms.yml \
  --stack-name soulcore-alarms-$STAGE \
  --parameter-overrides \
    Stage=$STAGE \
    ApiName=$API_NAME \
    LambdaFunctionPrefix=$LAMBDA_PREFIX \
    NotificationEmail=$EMAIL \
  --capabilities CAPABILITY_IAM

if [ $? -eq 0 ]; then
    echo "✅ CloudWatch alarms deployed successfully!"
    echo ""
    echo "🔔 You will receive an email to confirm your subscription to alarm notifications."
    echo "   Please check your email and confirm the subscription."
else
    echo "❌ Failed to deploy CloudWatch alarms. Please check the errors above."
    exit 1
fi
