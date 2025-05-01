#!/bin/bash
# Start Anima CLI - Command Line Interface for SoulCore

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
python3 -c "import websockets" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Installing required Python modules..."
    pip install websockets pyttsx3 requests
fi

# Start the Anima CLI
echo "Starting Anima CLI..."
python3 mcp/anima_cli.py "$@"
