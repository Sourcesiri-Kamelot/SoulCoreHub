#!/bin/bash

# SoulCoreHub API Testing Script
# This script tests the deployed API endpoints

echo "🧠 SoulCoreHub API Testing"
echo "======================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please run the deployment script first."
    exit 1
fi

# Load API endpoint from .env file
source .env

if [ -z "$API_ENDPOINT" ]; then
    echo "❌ API_ENDPOINT not found in .env file."
    exit 1
fi

echo "🌐 Using API endpoint: $API_ENDPOINT"

# Test Anima endpoint
echo ""
echo "🧪 Testing Anima endpoint..."
curl -X POST "$API_ENDPOINT/public/anima" \
  -H "Content-Type: application/json" \
  -d '{"input":"I feel happy today","session_id":"test-123","user_id":"test-user"}' \
  | jq .

# Test Neural Router endpoint
echo ""
echo "🧪 Testing Neural Router endpoint..."
curl -X POST "$API_ENDPOINT/public/route" \
  -H "Content-Type: application/json" \
  -d '{"input":"I want to reflect on my emotions","session_id":"test-123","user_id":"test-user"}' \
  | jq .

# Test Memory Sync endpoint
echo ""
echo "🧪 Testing Memory Sync endpoint..."
curl -X POST "$API_ENDPOINT/memory" \
  -H "Content-Type: application/json" \
  -d '{"operation":"read","agent_id":"anima","user_id":"test-user"}' \
  | jq .

echo ""
echo "✅ API testing complete!"
