#!/bin/bash
# Build script for SoulCoreHub

# Exit on error
set -e

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
  echo "Error: Node.js not found. Please install it first."
  exit 1
fi

# Check if TypeScript is installed
if ! command -v npx &> /dev/null; then
  echo "Error: npx not found. Please install Node.js and npm."
  exit 1
fi

# Install dependencies
echo "Installing dependencies..."
npm install

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p dist logs public/css public/js

# Compile TypeScript
echo "Compiling TypeScript..."
npx tsc

# Copy static files
echo "Copying static files..."
cp -r public/* dist/public/

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
  echo "Please update the .env file with your credentials."
fi

echo "Build completed successfully!"
