#!/bin/bash

# Run the SoulCoreHub RAG + MCP System
# This script starts the Flask server for the Soul Command Center

echo "Starting SoulCoreHub RAG + MCP System..."

# Create necessary directories if they don't exist
mkdir -p rag_vector_db
mkdir -p templates
mkdir -p static

# Make sure the script is executable
chmod +x mcp_client_bridge.py
chmod +x neural_routing.py
chmod +x app.py

# Start the Flask server
echo "Starting Flask server..."
python3 app.py
