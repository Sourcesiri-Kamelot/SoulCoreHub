#!/bin/bash
# start_evove.sh - Script to start the EvoVe autonomous system

# Set the base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR" || exit 1

# Create necessary directories
mkdir -p "$BASE_DIR/logs"
mkdir -p "$BASE_DIR/evove"
mkdir -p "$BASE_DIR/modules"

# Ensure Python environment is available
if [ -d "$BASE_DIR/myenv" ]; then
    echo "Activating Python virtual environment..."
    source "$BASE_DIR/myenv/bin/activate"
fi

# Install required packages if needed
echo "Checking for required packages..."
pip install psutil websockets pyttsx3 2>/dev/null

# Ensure permissions are set correctly
echo "Setting permissions..."
chmod +x "$BASE_DIR/maintain_permissions.sh"
bash "$BASE_DIR/maintain_permissions.sh"

# Check if MCP server is running
echo "Checking MCP server status..."
if ! pgrep -f "python.*mcp_main.py" > /dev/null; then
    echo "Starting MCP server..."
    cd "$BASE_DIR/mcp" && python mcp_main.py > "$BASE_DIR/logs/mcp_server.log" 2>&1 &
    sleep 2
fi

# Start EvoVe
echo "Starting EvoVe autonomous system..."
if [ -f "$BASE_DIR/evove/evove_autonomous.py" ]; then
    # Use the version in the evove directory
    python "$BASE_DIR/evove/evove_autonomous.py" "$@" > "$BASE_DIR/logs/evove.log" 2>&1 &
elif [ -f "$BASE_DIR/evove_autonomous.py" ]; then
    # Use the version in the main directory
    python "$BASE_DIR/evove_autonomous.py" "$@" > "$BASE_DIR/logs/evove.log" 2>&1 &
else
    echo "Error: EvoVe autonomous system not found"
    exit 1
fi

# Check if EvoVe started successfully
sleep 2
if pgrep -f "python.*evove_autonomous.py" > /dev/null; then
    echo "EvoVe autonomous system started successfully"
    echo "Log file: $BASE_DIR/logs/evove.log"
else
    echo "Error: Failed to start EvoVe autonomous system"
    echo "Check the log file for details: $BASE_DIR/logs/evove.log"
    exit 1
fi
