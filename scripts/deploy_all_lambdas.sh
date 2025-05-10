#!/bin/bash

# SoulCoreHub Full Lambda Deployment Script
# This script prepares and deploys all Lambda functions

echo "🧠 SoulCoreHub Full Lambda Deployment"
echo "=================================="

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI is not installed. Please install it first."
    echo "   Visit: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html"
    exit 1
fi

# Check if the functions directory exists
if [ ! -d "functions" ]; then
    echo "❌ functions directory not found. Please make sure you're in the correct directory."
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p memory
mkdir -p config

# Prepare each Lambda function
echo "📦 Preparing Lambda functions..."

# Function to prepare a Lambda package
prepare_lambda() {
    local function_name=$1
    local core_files=("${@:2}")
    
    echo "📦 Preparing $function_name Lambda function..."
    
    # Create a temporary directory for the Lambda package
    TEMP_DIR=$(mktemp -d)
    echo "📁 Created temporary directory: $TEMP_DIR"
    
    # Copy the Lambda function code
    cp functions/$function_name/app.py $TEMP_DIR/
    cp functions/$function_name/requirements.txt $TEMP_DIR/
    
    # Copy any additional files
    for file in "${core_files[@]}"; do
        cp $file $TEMP_DIR/ 2>/dev/null || echo "⚠️ $file not found, skipping"
    done
    
    # Create necessary directories
    mkdir -p $TEMP_DIR/logs
    mkdir -p $TEMP_DIR/memory
    mkdir -p $TEMP_DIR/config
    
    # Install dependencies
    echo "📦 Installing dependencies for $function_name..."
    pip install -r $TEMP_DIR/requirements.txt -t $TEMP_DIR
    
    # Build the Lambda package
    echo "📦 Building Lambda package for $function_name..."
    cd $TEMP_DIR
    zip -r ../${function_name}_lambda.zip .
    cd -
    
    # Move the package to the functions directory
    mv ${function_name}_lambda.zip functions/$function_name/
    
    echo "✅ $function_name Lambda package created: functions/$function_name/${function_name}_lambda.zip"
    
    # Clean up
    rm -rf $TEMP_DIR
}

# Prepare Anima Lambda
prepare_lambda "anima" "anima_autonomous.py" "anima_memory_bridge.py" "anima_model_router.py" "anima_nlp_intent.py" "anima_huggingface_connector.py" "functions/anima/anima_lambda_adapter.py"

# Prepare Neural Router Lambda
prepare_lambda "neural_router"

# Prepare Memory Sync Lambda
prepare_lambda "memory_sync"

# Prepare GPTSoul Lambda (if it exists)
if [ -d "functions/gptsoul" ]; then
    prepare_lambda "gptsoul" "gptsoul_soulconfig.py" "memory_system.py"
fi

# Prepare Resurrection Lambda (if it exists)
if [ -d "functions/resurrection" ]; then
    prepare_lambda "resurrection" "agent_resurrection.py"
fi

# Build the SAM application
echo "🚀 Building SAM application..."
sam build --use-container --cached

# Deploy the SAM application
echo "🚀 Deploying SAM application..."
sam deploy --config-env evolve

echo "✅ Full Lambda deployment completed!"
