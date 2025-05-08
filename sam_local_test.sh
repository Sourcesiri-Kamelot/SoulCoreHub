#!/bin/bash

# SoulCoreHub SAM Local Test Script
# This script starts the SAM local API for testing

echo "🧠 SoulCoreHub SAM Local Test"
echo "============================"

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI is not installed. Please install it first."
    echo "   Visit: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html"
    exit 1
fi

# Check if the .aws-sam directory exists (created by sam build)
if [ ! -d ".aws-sam" ]; then
    echo "❌ Build artifacts not found. Please run './sam_build.sh' first."
    exit 1
fi

# Set environment variables for local testing
export MEMORY_BUCKET="local-memory-bucket"

echo "🚀 Starting SAM local API..."
echo "  API will be available at: http://127.0.0.1:3000"
echo "  Press Ctrl+C to stop the API"
echo ""

sam local start-api --warm-containers EAGER

# This script will continue running until the user presses Ctrl+C
