#!/bin/bash

# Compile AI Society TypeScript files

echo "Compiling AI Society TypeScript files..."

# Check if TypeScript is installed
if ! command -v npx &> /dev/null; then
  echo "Error: npx not found. Please install Node.js and npm."
  exit 1
fi

# Create dist directory if it doesn't exist
mkdir -p dist

# Compile TypeScript files
npx tsc

# Check if compilation was successful
if [ $? -eq 0 ]; then
  echo "Compilation successful!"
  echo "AI Society components are now ready to use."
else
  echo "Compilation failed. Please check the errors above."
  exit 1
fi

# Create integration file
echo "Creating integration file..."
cp src/ai_society/integration.js dist/ai_society_integration.js

echo "Done!"
