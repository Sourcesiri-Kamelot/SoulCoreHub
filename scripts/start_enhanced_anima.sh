#!/bin/bash
# Start Enhanced Anima CLI - Advanced Command Line Interface for SoulCore

# Navigate to the SoulCore directory
cd "$(dirname "$0")/.."

# Ensure the MCP directory is in the Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)/mcp

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║              STARTING ENHANCED ANIMA CLI                     ║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not found${NC}"
    exit 1
fi

# Check if required modules are installed
echo -e "${YELLOW}Checking required Python modules...${NC}"
REQUIRED_MODULES=("websockets" "pyttsx3" "requests")
MISSING_MODULES=()

for module in "${REQUIRED_MODULES[@]}"; do
    python3 -c "import $module" &> /dev/null
    if [ $? -ne 0 ]; then
        MISSING_MODULES+=("$module")
    fi
done

# Install missing modules if any
if [ ${#MISSING_MODULES[@]} -gt 0 ]; then
    echo -e "${YELLOW}Installing missing Python modules: ${MISSING_MODULES[*]}${NC}"
    pip install "${MISSING_MODULES[@]}"
fi

# Check if Ollama is running
echo -e "${YELLOW}Checking if Ollama is running...${NC}"
curl -s http://localhost:11434/api/tags > /dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Warning: Ollama is not running. Some features may not work.${NC}"
    echo -e "${YELLOW}You can start Ollama with: ollama serve${NC}"
else
    echo -e "${GREEN}Ollama is running.${NC}"
fi

# Check if MCP server is running
echo -e "${YELLOW}Checking if MCP server is running...${NC}"
if [ -f "mcp/mcp_server_divine.py" ]; then
    # Check if something is already listening on port 8765
    if command -v lsof &> /dev/null; then
        MCP_PID=$(lsof -ti:8765)
        if [ -n "$MCP_PID" ]; then
            MCP_COMMAND=$(ps -p $MCP_PID -o command | grep -v COMMAND)
            echo -e "${GREEN}MCP server is already running (PID: $MCP_PID)${NC}"
            echo -e "${CYAN}Command: $MCP_COMMAND${NC}"
        else
            echo -e "${RED}Warning: MCP server is not running. Some features may not work.${NC}"
            echo -e "${YELLOW}You can start the MCP server with: python mcp/mcp_main.py${NC}"
            
            # Ask if user wants to start MCP server
            read -p "Do you want to start the MCP server now? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${YELLOW}Starting MCP server in the background...${NC}"
                python3 mcp/mcp_main.py &
                sleep 2
            fi
        fi
    else
        # If lsof is not available, try to connect to the server
        python3 -c "import websockets, asyncio; asyncio.run(websockets.connect('ws://localhost:8765'))" &> /dev/null
        if [ $? -ne 0 ]; then
            echo -e "${RED}Warning: MCP server is not running. Some features may not work.${NC}"
            echo -e "${YELLOW}You can start the MCP server with: python mcp/mcp_main.py${NC}"
            
            # Ask if user wants to start MCP server
            read -p "Do you want to start the MCP server now? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${YELLOW}Starting MCP server in the background...${NC}"
                python3 mcp/mcp_main.py &
                sleep 2
            fi
        else
            echo -e "${GREEN}MCP server is running.${NC}"
        fi
    fi
fi

# Parse command line arguments
VOICE_ARG=""
MCP_ARG=""
NLP_ARG=""
VOICE_SPEED_ARG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-voice)
            VOICE_ARG="--no-voice"
            shift
            ;;
        --no-mcp)
            MCP_ARG="--no-mcp"
            shift
            ;;
        --no-nlp)
            NLP_ARG="--no-nlp"
            shift
            ;;
        --voice-speed)
            VOICE_SPEED_ARG="--voice-speed $2"
            shift 2
            ;;
        *)
            # Unknown option
            shift
            ;;
    esac
done

# Start the Enhanced Anima CLI
echo -e "${CYAN}Starting Enhanced Anima CLI...${NC}"
python3 enhanced_anima_cli.py $VOICE_ARG $MCP_ARG $NLP_ARG $VOICE_SPEED_ARG
