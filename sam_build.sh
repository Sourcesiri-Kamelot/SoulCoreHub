#!/bin/bash

# SoulCoreHub SAM Build Script
# This script builds the SAM application for deployment

echo "🧠 SoulCoreHub SAM Build"
echo "========================"

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI is not installed. Please install it first."
    echo "   Visit: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html"
    exit 1
fi

# Check if template.yaml exists
if [ ! -f "template.yaml" ]; then
    echo "❌ template.yaml not found. Please make sure you're in the correct directory."
    exit 1
fi

echo "📦 Building SAM application..."
sam build

if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
    echo ""
    echo "Next steps:"
    echo "  - Run './sam_local_test.sh' to test locally"
    echo "  - Run './sam_deploy.sh' to deploy to AWS"
else
    echo "❌ Build failed. Please check the errors above."
fi
