#!/bin/bash
# start_dashboard.sh - Script to start the SoulCore dashboard

# Set the base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR" || exit 1

# Create logs directory if it doesn't exist
mkdir -p "$BASE_DIR/logs/dashboard"

echo "Starting SoulCore Dashboard..."

# Kill any existing dashboard server
pkill -f "node.*soulcore_dashboard_server.js" 2>/dev/null

# Start the dashboard server
node "$BASE_DIR/soulcore_dashboard_server.js" > "$BASE_DIR/logs/dashboard/dashboard_server.log" 2>&1 &

# Wait for the server to start
sleep 2

# Check if the server is running
if pgrep -f "node.*soulcore_dashboard_server.js" > /dev/null; then
    echo "SoulCore Dashboard server started successfully"
    echo "Open your browser and navigate to http://localhost:3000"
    
    # Try to open the browser automatically
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "http://localhost:3000"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        xdg-open "http://localhost:3000" &> /dev/null || true
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        start "http://localhost:3000" || true
    fi
else
    echo "Error: Failed to start SoulCore Dashboard server"
    echo "Check the log file for details: $BASE_DIR/logs/dashboard/dashboard_server.log"
    exit 1
fi
