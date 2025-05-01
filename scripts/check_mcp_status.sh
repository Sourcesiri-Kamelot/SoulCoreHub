#!/bin/bash
# Check MCP server status and provide management options

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║                  MCP SERVER STATUS CHECK                     ║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"

# Check if lsof is available
if ! command -v lsof &> /dev/null; then
    echo -e "${RED}Error: 'lsof' command not found. Please install it to use this script.${NC}"
    exit 1
fi

# Check if something is listening on port 8765
MCP_PID=$(lsof -ti:8765)

if [ -n "$MCP_PID" ]; then
    # MCP server is running
    MCP_COMMAND=$(ps -p $MCP_PID -o command | grep -v COMMAND)
    echo -e "${GREEN}MCP server is running with PID: $MCP_PID${NC}"
    echo -e "${CYAN}Command: $MCP_COMMAND${NC}"
    
    # Show uptime if possible
    if [ -d "/proc/$MCP_PID" ]; then
        # Linux
        START_TIME=$(stat -c %Y /proc/$MCP_PID)
        CURRENT_TIME=$(date +%s)
        UPTIME=$((CURRENT_TIME - START_TIME))
        
        # Convert seconds to days, hours, minutes, seconds
        DAYS=$((UPTIME / 86400))
        HOURS=$(( (UPTIME % 86400) / 3600 ))
        MINUTES=$(( (UPTIME % 3600) / 60 ))
        SECONDS=$((UPTIME % 60))
        
        echo -e "${CYAN}Uptime: ${DAYS}d ${HOURS}h ${MINUTES}m ${SECONDS}s${NC}"
    else
        # macOS or other Unix
        PS_TIME=$(ps -p $MCP_PID -o etime | grep -v ELAPSED)
        echo -e "${CYAN}Uptime: $PS_TIME${NC}"
    fi
    
    # Show options
    echo
    echo -e "${YELLOW}Options:${NC}"
    echo -e "  ${CYAN}1. Stop MCP server${NC}"
    echo -e "  ${CYAN}2. Restart MCP server${NC}"
    echo -e "  ${CYAN}3. View MCP server logs${NC}"
    echo -e "  ${CYAN}4. Exit${NC}"
    
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            echo -e "${YELLOW}Stopping MCP server...${NC}"
            kill $MCP_PID
            sleep 2
            if kill -0 $MCP_PID 2>/dev/null; then
                echo -e "${RED}Failed to stop MCP server. Trying SIGKILL...${NC}"
                kill -9 $MCP_PID
                sleep 1
                if kill -0 $MCP_PID 2>/dev/null; then
                    echo -e "${RED}Failed to stop MCP server with SIGKILL.${NC}"
                else
                    echo -e "${GREEN}MCP server stopped.${NC}"
                fi
            else
                echo -e "${GREEN}MCP server stopped.${NC}"
            fi
            ;;
        2)
            echo -e "${YELLOW}Restarting MCP server...${NC}"
            kill $MCP_PID
            sleep 2
            if kill -0 $MCP_PID 2>/dev/null; then
                echo -e "${RED}Failed to stop MCP server. Trying SIGKILL...${NC}"
                kill -9 $MCP_PID
                sleep 1
            fi
            
            echo -e "${YELLOW}Starting MCP server...${NC}"
            cd "$(dirname "$0")/.."
            python3 mcp/mcp_main.py &
            sleep 2
            
            NEW_PID=$(lsof -ti:8765)
            if [ -n "$NEW_PID" ]; then
                echo -e "${GREEN}MCP server restarted with PID: $NEW_PID${NC}"
            else
                echo -e "${RED}Failed to restart MCP server.${NC}"
            fi
            ;;
        3)
            echo -e "${YELLOW}MCP server logs:${NC}"
            if [ -f "soulcore_mcp.log" ]; then
                tail -n 50 soulcore_mcp.log
            elif [ -f "mcp/soulcore_mcp.log" ]; then
                tail -n 50 mcp/soulcore_mcp.log
            elif [ -f "logs/soulcore_mcp.log" ]; then
                tail -n 50 logs/soulcore_mcp.log
            else
                echo -e "${RED}MCP server log file not found.${NC}"
            fi
            ;;
        4)
            echo -e "${GREEN}Exiting...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice.${NC}"
            ;;
    esac
else
    # MCP server is not running
    echo -e "${RED}MCP server is not running.${NC}"
    
    # Show options
    echo
    echo -e "${YELLOW}Options:${NC}"
    echo -e "  ${CYAN}1. Start MCP server${NC}"
    echo -e "  ${CYAN}2. Exit${NC}"
    
    read -p "Enter your choice (1-2): " choice
    
    case $choice in
        1)
            echo -e "${YELLOW}Starting MCP server...${NC}"
            cd "$(dirname "$0")/.."
            python3 mcp/mcp_main.py &
            sleep 2
            
            NEW_PID=$(lsof -ti:8765)
            if [ -n "$NEW_PID" ]; then
                echo -e "${GREEN}MCP server started with PID: $NEW_PID${NC}"
            else
                echo -e "${RED}Failed to start MCP server.${NC}"
            fi
            ;;
        2)
            echo -e "${GREEN}Exiting...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice.${NC}"
            ;;
    esac
fi
