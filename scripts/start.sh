#!/bin/bash
# Start script for SoulCoreHub

# Exit on error
set -e

# Check if Ollama is running
echo "Checking if Ollama is running..."
if ! curl -s http://localhost:11434/api/version > /dev/null; then
  echo "Ollama is not running. Starting Ollama..."
  ollama serve &
  sleep 5
fi

# Check if soulfamily model is available
echo "Checking if soulfamily model is available..."
if ! ollama list | grep -q "soulfamily"; then
  echo "soulfamily model not found. Please make sure it's installed."
  echo "You can install it with: ollama pull soulfamily:latest"
  exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
  echo "Please update the .env file with your credentials."
fi

# Check if TypeScript files are compiled
if [ ! -d "dist" ] || [ ! -f "dist/server.js" ]; then
  echo "TypeScript files not compiled. Compiling..."
  ./scripts/build.sh
fi

# Start the server
echo "Starting SoulCoreHub..."
node dist/server.js
