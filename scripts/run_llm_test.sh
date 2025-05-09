#!/bin/bash

# Run LLM Test
# This script compiles and runs the LLM test

# Exit on error
set -e

# Check if TypeScript is installed
if ! command -v npx &> /dev/null; then
  echo "Error: npx not found. Please install Node.js and npm."
  exit 1
fi

# Create dist directory if it doesn't exist
mkdir -p dist

# Compile TypeScript files
echo "Compiling TypeScript files..."
npx tsc

# Check if compilation was successful
if [ $? -eq 0 ]; then
  echo "Compilation successful!"
else
  echo "Compilation failed. Please check the errors above."
  exit 1
fi

# Run LLM test
echo "Running LLM test..."
node dist/llm/llm_test.js
