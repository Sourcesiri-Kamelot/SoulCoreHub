#!/bin/bash

# SoulCoreHub Simplified Deployment Script
# This script builds and deploys the SoulCoreHub serverless application

echo "🧠 SoulCoreHub Simplified Deployment"
echo "=================================="

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI is not installed. Please install it first."
    echo "   Visit: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Build the SAM application
echo "🚀 Building SAM application..."
sam build

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Please check the errors above."
    exit 1
fi

echo "✅ Build completed successfully!"

# Deploy the SAM application
echo "🚀 Deploying SAM application..."
sam deploy --config-env evolve

if [ $? -ne 0 ]; then
    echo "❌ Deployment failed. Please check the errors above."
    exit 1
fi

echo "✅ Deployment completed successfully!"

# Get the API Gateway URL
API_URL=$(aws cloudformation describe-stacks --stack-name soulcore-hub --query "Stacks[0].Outputs[?OutputKey=='SoulCoreApi'].OutputValue" --output text)

if [ ! -z "$API_URL" ]; then
    echo ""
    echo "🌐 SoulCore API is now available at: $API_URL"
    
    # Save the API URL to .env file
    if [ -f ".env" ]; then
        if grep -q "API_ENDPOINT" .env; then
            sed -i '' "s|API_ENDPOINT=.*|API_ENDPOINT=$API_URL|g" .env
        else
            echo "API_ENDPOINT=$API_URL" >> .env
        fi
    else
        echo "API_ENDPOINT=$API_URL" > .env
    fi
    
    echo "✅ API URL saved to .env file"
fi

echo ""
echo "🎉 SoulCoreHub deployment complete!"
