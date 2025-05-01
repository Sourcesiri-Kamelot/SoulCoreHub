#!/bin/bash

# PaulterPan Trading Signal Bot Launcher
# This script starts the PaulterPan trading signal bot

# Set up environment
echo "Setting up PaulterPan environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install or update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p data/cache

# Run the bot
echo "Starting PaulterPan Trading Signal Bot..."
python src/main.py

# Deactivate virtual environment on exit
deactivate
