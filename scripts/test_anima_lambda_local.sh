#!/bin/bash

# SoulCoreHub Anima Lambda Local Testing Script
# This script tests the Anima Lambda function locally

echo "🧠 SoulCoreHub Anima Lambda Local Testing"
echo "======================================"

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI is not installed. Please install it first."
    echo "   Visit: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html"
    exit 1
fi

# Check if the functions directory exists
if [ ! -d "functions/anima" ]; then
    echo "❌ functions/anima directory not found. Please make sure you're in the correct directory."
    exit 1
fi

echo "🚀 Invoking Anima Lambda function locally..."

# Set environment variables for local testing
export MEMORY_BUCKET="soulcore-memory-local"
export STAGE="dev"

# Invoke the Lambda function
sam local invoke AnimaLambda -e functions/anima/event.json

echo "✅ Local testing completed!"
