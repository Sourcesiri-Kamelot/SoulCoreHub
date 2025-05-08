#!/bin/bash
# update_agent_hub.sh - Update the agent response hub to use the enhanced version

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Navigate to the SoulCoreHub directory
cd "$(dirname "$0")" || exit 1

echo -e "${YELLOW}Updating agent response hub to use LLM-powered conversations...${NC}"

# Backup the original file
if [ -f "agent_response_hub.py" ]; then
    echo -e "${YELLOW}Backing up original agent_response_hub.py...${NC}"
    cp agent_response_hub.py agent_response_hub.py.bak
    echo -e "${GREEN}Backup created: agent_response_hub.py.bak${NC}"
fi

# Copy the enhanced version to the main file
if [ -f "agent_response_hub_enhanced.py" ]; then
    echo -e "${YELLOW}Updating agent_response_hub.py with enhanced version...${NC}"
    cp agent_response_hub_enhanced.py agent_response_hub.py
    echo -e "${GREEN}Update complete!${NC}"
else
    echo -e "${RED}Error: agent_response_hub_enhanced.py not found${NC}"
    exit 1
fi

# Make sure it's executable
chmod +x agent_response_hub.py

echo -e "${GREEN}Agent response hub has been updated to use LLM-powered conversations${NC}"
echo -e "${YELLOW}You can now use the dashboard's 'Ask Anima' button to have real conversations${NC}"
echo -e "${YELLOW}Or run: python test_anima_conversation.py${NC}"
