#!/bin/bash
# SoulCoreHub - Stop Hugging Face Bridge
# This script stops the Hugging Face Bridge server

# Set the directory to the script's location
cd "$(dirname "$0")/.."

# Check if PID file exists
if [ -f .huggingface_bridge.pid ]; then
    PID=$(cat .huggingface_bridge.pid)
    
    # Check if process is running
    if ps -p $PID > /dev/null; then
        echo "Stopping Hugging Face Bridge Server (PID: $PID)..."
        kill $PID
        
        # Wait for process to terminate
        sleep 2
        
        # Check if process is still running
        if ps -p $PID > /dev/null; then
            echo "Process did not terminate gracefully. Forcing termination..."
            kill -9 $PID
        fi
        
        echo "Hugging Face Bridge Server stopped."
    else
        echo "Hugging Face Bridge Server is not running."
    fi
    
    # Remove PID file
    rm .huggingface_bridge.pid
else
    echo "Hugging Face Bridge Server is not running or PID file not found."
fi
