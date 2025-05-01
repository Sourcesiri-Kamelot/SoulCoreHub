#!/bin/bash
# Start Anima CLI with internet access

# Navigate to the SoulCore directory
cd "$(dirname "$0")/.."

# Ensure the MCP directory is in the Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)/mcp

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found"
    exit 1
fi

# Check if required modules are installed
python3 -c "import requests" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Installing required Python modules..."
    bash scripts/install_dependencies.sh
fi

# Check for API keys in environment variables
if [ -z "$SERP_API_KEY" ] && [ -z "$NEWSAPI_KEY" ] && [ -z "$WEATHER_API_KEY" ]; then
    # Check for API keys in config file
    if [ -f "config/api_keys.json" ]; then
        echo "Using API keys from config file"
    else
        echo "Warning: No API keys found. Internet access will be limited."
        echo "Consider setting up API keys for full functionality."
        echo "See README_ANIMA_INTERNET.md for details."
    fi
fi

# Start the MCP server
echo "Starting MCP server with internet access..."
python3 mcp/mcp_main.py &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for MCP server to initialize..."
sleep 3

# Start the Anima CLI
echo "Starting Anima CLI..."
python3 mcp/anima_cli.py "$@"

# Clean up
kill $SERVER_PID
