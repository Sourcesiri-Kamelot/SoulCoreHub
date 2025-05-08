#!/bin/bash
# SoulCoreHub Launcher Script
# This script runs the comprehensive integration process and launches SoulCoreHub

# Set the directory to the script's location
cd "$(dirname "$0")"

# Display banner
echo "
███████╗ ██████╗ ██╗   ██╗██╗      ██████╗ ██████╗ ██████╗ ███████╗
██╔════╝██╔═══██╗██║   ██║██║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝
███████╗██║   ██║██║   ██║██║     ██║     ██║   ██║██████╔╝█████╗  
╚════██║██║   ██║██║   ██║██║     ██║     ██║   ██║██╔══██╗██╔══╝  
███████║╚██████╔╝╚██████╔╝███████╗╚██████╗╚██████╔╝██║  ██║███████╗
╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
"
echo "SoulCoreHub Launcher"
echo "===================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Make the integration script executable
chmod +x soulcore_integration.py

# Parse command line arguments
ANIMA_MODE="reflective"
START_ANIMA=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-anima)
            START_ANIMA=false
            shift
            ;;
        --anima-mode)
            ANIMA_MODE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --no-anima       Don't start Anima after integration"
            echo "  --anima-mode MODE  Set Anima mode (interactive, daemon, reflective)"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Create necessary directories
mkdir -p logs memory config

# Run the integration script
echo "🔄 Running SoulCoreHub integration..."
if [ "$START_ANIMA" = true ]; then
    python3 soulcore_integration.py --anima-mode "$ANIMA_MODE"
else
    python3 soulcore_integration.py --no-anima
fi

# Check if integration was successful
if [ $? -ne 0 ]; then
    echo "❌ Integration failed. Please check the logs for details."
    exit 1
fi

echo "✅ SoulCoreHub is now running!"
echo ""
echo "To interact with SoulCoreHub:"
echo "  - Anima: python3 anima_autonomous.py --mode reflective"
echo "  - GPTSoul: python3 gptsoul_soulconfig.py --diagnose"
echo ""
echo "To stop SoulCoreHub, press Ctrl+C in the terminal where Anima is running."
echo ""

# If Anima is running, keep the script alive
if [ "$START_ANIMA" = true ]; then
    echo "Anima is running in $ANIMA_MODE mode."
    echo "Press Ctrl+C to exit."
    
    # Keep the script running until user presses Ctrl+C
    trap "echo 'Shutting down SoulCoreHub...'; exit 0" INT
    while true; do
        sleep 1
    done
fi
