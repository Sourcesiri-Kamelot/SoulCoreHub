#!/bin/bash

# SoulCoreHub Anima Lambda Deployment Script
# This script prepares and deploys the Anima Lambda function

echo "🧠 SoulCoreHub Anima Lambda Deployment"
echo "====================================="

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

echo "📦 Preparing Anima Lambda function..."

# Create a temporary directory for the Lambda package
TEMP_DIR=$(mktemp -d)
echo "📁 Created temporary directory: $TEMP_DIR"

# Copy the Lambda function code
cp functions/anima/app.py $TEMP_DIR/
cp functions/anima/anima_lambda_adapter.py $TEMP_DIR/
cp functions/anima/requirements.txt $TEMP_DIR/

# Copy the core Anima files
cp anima_autonomous.py $TEMP_DIR/
cp anima_memory_bridge.py $TEMP_DIR/
cp anima_model_router.py $TEMP_DIR/ 2>/dev/null || echo "⚠️ anima_model_router.py not found, skipping"
cp anima_nlp_intent.py $TEMP_DIR/ 2>/dev/null || echo "⚠️ anima_nlp_intent.py not found, skipping"
cp anima_huggingface_connector.py $TEMP_DIR/ 2>/dev/null || echo "⚠️ anima_huggingface_connector.py not found, skipping"

# Create necessary directories
mkdir -p $TEMP_DIR/logs
mkdir -p $TEMP_DIR/memory
mkdir -p $TEMP_DIR/config

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r $TEMP_DIR/requirements.txt -t $TEMP_DIR

# Build the Lambda package
echo "📦 Building Lambda package..."
cd $TEMP_DIR
zip -r ../anima_lambda.zip .
cd -

# Move the package to the functions directory
mv anima_lambda.zip functions/anima/

echo "✅ Anima Lambda package created: functions/anima/anima_lambda.zip"

# Build the SAM application
echo "🚀 Building SAM application..."
sam build --use-container --cached

# Deploy the SAM application
echo "🚀 Deploying SAM application..."
sam deploy --config-env evolve

# Clean up
echo "🧹 Cleaning up..."
rm -rf $TEMP_DIR

echo "✅ Anima Lambda deployment completed!"
