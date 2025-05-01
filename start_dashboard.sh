#!/bin/bash

# Start the SoulCore Dashboard
echo "Starting SoulCore Dashboard..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js to run the dashboard."
    exit 1
fi

# Check if Express is installed
if ! npm list express | grep -q express; then
    echo "Installing Express..."
    npm install express
fi

# Start the dashboard server
node soulcore_dashboard_server.js

echo "SoulCore Dashboard started at http://localhost:3000"
