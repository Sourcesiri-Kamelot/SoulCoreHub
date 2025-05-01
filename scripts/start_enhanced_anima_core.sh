#!/bin/bash
# Start Enhanced Anima Core - Advanced capabilities for Anima

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Navigate to the SoulCore directory
cd "$(dirname "$0")/.."

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║              STARTING ENHANCED ANIMA CORE                    ║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║  Advanced capabilities for Anima with:                       ║${NC}"
echo -e "${BLUE}║  - Hierarchical memory with emotional tagging                ║${NC}"
echo -e "${BLUE}║  - Dynamic voice with multiple personalities                 ║${NC}"
echo -e "${BLUE}║  - Multimodal integration (image/audio)                      ║${NC}"
echo -e "${BLUE}║  - Autonomous learning                                       ║${NC}"
echo -e "${BLUE}║  - Enhanced MCP integration                                  ║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not found${NC}"
    exit 1
fi

# Check if required modules are installed
echo -e "${YELLOW}Checking required Python modules...${NC}"
REQUIRED_MODULES=("websockets" "pyttsx3" "requests" "numpy" "pillow" "sounddevice" "soundfile" "librosa" "nltk")
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

# Create anima directory if it doesn't exist
if [ ! -d "anima" ]; then
    echo -e "${YELLOW}Creating anima directory...${NC}"
    mkdir -p anima
fi

# Check if MCP server is running
echo -e "${YELLOW}Checking if MCP server is running...${NC}"
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

# Check if Ollama is running
echo -e "${YELLOW}Checking if Ollama is running...${NC}"
curl -s http://localhost:11434/api/tags > /dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Warning: Ollama is not running. Some features may not work.${NC}"
    echo -e "${YELLOW}You can start Ollama with: ollama serve${NC}"
else
    echo -e "${GREEN}Ollama is running.${NC}"
fi

# Parse command line arguments
VOICE_ARG=""
MULTIMODAL_ARG=""
LEARNING_ARG=""
INTERACTIVE_ARG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-voice)
            VOICE_ARG="--no-voice"
            shift
            ;;
        --no-multimodal)
            MULTIMODAL_ARG="--no-multimodal"
            shift
            ;;
        --no-learning)
            LEARNING_ARG="--no-learning"
            shift
            ;;
        --interactive)
            INTERACTIVE_ARG="--interactive"
            shift
            ;;
        *)
            # Unknown option
            shift
            ;;
    esac
done

# Start the Enhanced Anima Core
echo -e "${CYAN}Starting Enhanced Anima Core...${NC}"
python3 -c "
import sys
sys.path.append('anima')
from anima_enhanced_core import AnimaEnhancedCore

# Create and start Anima
anima = AnimaEnhancedCore()

# Configure based on arguments
if '$VOICE_ARG' == '--no-voice':
    anima.enable_voice(False)
    print('Voice disabled')

if '$MULTIMODAL_ARG' == '--no-multimodal':
    anima.enable_multimodal(False)
    print('Multimodal integration disabled')

if '$LEARNING_ARG' == '--no-learning':
    anima.enable_autonomous_learning(False)
    print('Autonomous learning disabled')

# Start Anima
print('Starting Anima enhanced core...')
anima.start()

# Interactive mode
if '$INTERACTIVE_ARG' == '--interactive':
    print('\\nEntering interactive mode. Type \\'exit\\' to quit.')
    while True:
        try:
            user_input = input('\\nYou> ')
            if user_input.lower() in ['exit', 'quit', 'bye']:
                break
            response = anima.process_input(user_input)
            print(f'Anima> {response}')
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f'Error: {e}')
    
    # Stop Anima before exiting
    print('\\nStopping Anima enhanced core...')
    anima.stop()
else:
    print('\\nAnima enhanced core is running in the background.')
    print('Use the API to interact with it.')
    
    # Keep the script running
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print('\\nStopping Anima enhanced core...')
        anima.stop()
"
