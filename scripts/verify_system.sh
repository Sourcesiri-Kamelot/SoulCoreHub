#!/bin/bash
# System verification script for SoulCoreHub

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

cd "$(dirname "$0")/.." || exit 1

echo -e "${BLUE}SoulCoreHub System Verification${NC}"
echo "=============================="

echo -e "\n${YELLOW}Checking agent status...${NC}"

check_process() {
    if pgrep -f "$1" > /dev/null; then
        echo -e "${GREEN}✓ $2 is running${NC}"
    else
        echo -e "${RED}✗ $2 is not running${NC}"
    fi
}

check_process "anima_autonomous.py" "Anima Core"
check_process "server.js" "Web Interface"
check_process "mcp_main.py" "MCP Server"

echo -e "\n${YELLOW}Checking MCP agent registration...${NC}"
if [ -f "logs/mcp_main.log" ]; then
    REGISTERED_AGENTS=$(grep "Agent registered:" logs/mcp_main.log | wc -l)
    echo -e "${GREEN}✓ $REGISTERED_AGENTS agents registered with MCP${NC}"
else
    echo -e "${RED}✗ MCP log file not found${NC}"
fi

echo -e "\n${YELLOW}Checking for errors in logs...${NC}"
ERROR_COUNT=0
check_errors() {
    if [ -f "$1" ]; then
        local errors=$(grep -i "error\|exception\|failed" "$1" | wc -l)
        if [ "$errors" -gt 0 ]; then
            echo -e "${RED}✗ Found $errors errors in $1${NC}"
            ERROR_COUNT=$((ERROR_COUNT + errors))
        else
            echo -e "${GREEN}✓ No errors found in $1${NC}"
        fi
    else
        echo -e "${YELLOW}! Log file $1 not found${NC}"
    fi
}
check_errors "logs/anima_autonomous.log"
check_errors "logs/mcp_main.log"
check_errors "logs/orchestrator_interactions.log"
check_errors "logs/cpu_monitor.log"
check_errors "logs/email_agent.log"

echo -e "\n${YELLOW}Checking agent heartbeats...${NC}"
python -c "
import json, os
status_file = 'logs/agent_status.json'
if os.path.exists(status_file):
    with open(status_file, 'r') as f:
        try:
            data = json.load(f)
            healthy = sum(1 for agent in data.get('agent_health', {}).values() if agent == 'healthy')
            unhealthy = sum(1 for agent in data.get('agent_health', {}).values() if agent == 'unhealthy')
            print(f'\033[0;32m✓ {healthy} healthy agents\033[0m')
            if unhealthy > 0:
                print(f'\033[0;31m✗ {unhealthy} unhealthy agents\033[0m')
                for name, status in data.get('agent_health', {}).items():
                    if status == 'unhealthy':
                        print(f'\033[0;31m  - {name} is unhealthy\033[0m')
            else:
                print(f'\033[0;32m✓ All agents are healthy\033[0m')
        except json.JSONDecodeError:
            print('\033[0;31m✗ Invalid JSON in agent status file\033[0m')
else:
    print('\033[1;33m! Agent status file not found\033[0m')
"

echo -e "\n${BLUE}Verification Summary${NC}"
echo "=============================="
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo -e "${RED}Found $ERROR_COUNT errors in logs${NC}"
    echo -e "${YELLOW}Run the following commands to fix common issues:${NC}"
    echo "1. bash scripts/check_mcp_health.sh"
    echo "2. bash scripts/maintain_permissions.sh"
    echo "3. python agent_cli.py diagnose all"
else
    echo -e "${GREEN}System appears to be functioning correctly!${NC}"
fi

echo -e "\n${BLUE}To monitor the system:${NC}"
echo "1. python agent_cli.py status"
echo "2. tail -f logs/anima_autonomous.log"
echo "3. bash scripts/check_mcp_status.sh"
