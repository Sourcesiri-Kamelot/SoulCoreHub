#!/bin/bash
# SoulCoreHub - Start Hugging Face Bridge
# This script starts the Hugging Face Bridge server

# Set the directory to the script's location
cd "$(dirname "$0")/.."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js to use the Hugging Face Bridge."
    exit 1
fi

# Check if required packages are installed
if [ ! -d "node_modules/@huggingface" ]; then
    echo "Installing required Node.js packages..."
    npm install @huggingface/inference @huggingface/hub @huggingface/agents express
fi

# Create necessary directories
mkdir -p logs
mkdir -p public/generated_images

# Set environment variables
export HF_TOKEN="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"
export HF_BRIDGE_PORT=3456

# Start the bridge server
echo "Starting Hugging Face Bridge Server..."
node huggingface_bridge_server.js > logs/huggingface_bridge.log 2>&1 &

# Save the PID
echo $! > .huggingface_bridge.pid

echo "Hugging Face Bridge Server started with PID $(cat .huggingface_bridge.pid)"
echo "Logs are available at logs/huggingface_bridge.log"
