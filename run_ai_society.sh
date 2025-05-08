#!/bin/bash

# SoulCoreHub AI Society Runner Script
# This script runs the AI Society simulation and launches the visualization

# Set the base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_SOCIETY_DIR="$BASE_DIR/ai_society"

# Create data directory if it doesn't exist
mkdir -p "$AI_SOCIETY_DIR/data"

# Function to check if Python is installed
check_python() {
    if command -v python3 &>/dev/null; then
        echo "Python 3 is installed"
        return 0
    else
        echo "Python 3 is not installed. Please install Python 3 to run the AI Society simulation."
        return 1
    fi
}

# Function to check if required packages are installed
check_packages() {
    echo "Checking required packages..."
    python3 -c "import sys; packages = ['json', 'logging', 'argparse', 'uuid', 'time']; missing = [p for p in packages if p not in sys.modules and p not in ['json', 'logging', 'argparse']]; sys.exit(1 if missing else 0)" 2>/dev/null
    
    if [ $? -ne 0 ]; then
        echo "Installing required packages..."
        pip3 install argparse
        return $?
    fi
    
    return 0
}

# Function to run the simulation
run_simulation() {
    echo "Running AI Society simulation..."
    cd "$BASE_DIR"
    python3 -m ai_society.main --steps 20 --save --interval 0.5
    return $?
}

# Function to launch the visualization
launch_visualization() {
    echo "Launching AI Society visualization..."
    
    # Check if Python's HTTP server is available
    if command -v python3 &>/dev/null; then
        cd "$BASE_DIR"
        echo "Starting HTTP server on port 8000..."
        echo "Open your browser and navigate to http://localhost:8000/ai_society/visualization/"
        python3 -m http.server 8000
    else
        echo "Python 3 is not installed. Please open the visualization manually:"
        echo "$AI_SOCIETY_DIR/visualization/index.html"
    fi
}

# Main execution
echo "SoulCoreHub AI Society Runner"
echo "============================"

# Check requirements
check_python || exit 1
check_packages || exit 1

# Run simulation
run_simulation || exit 1

# Launch visualization
launch_visualization

echo "Done!"
