#!/bin/bash
# SoulCoreHub Container Run Script
# This script runs SoulCoreHub in a container environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  SoulCoreHub Container Run  ${NC}"
echo -e "${GREEN}=========================================${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating a sample one...${NC}"
    cp .env.example .env || echo -e "${YELLOW}No .env.example found, creating empty .env file${NC}"
    touch .env
    echo -e "${YELLOW}Please update the .env file with your credentials before proceeding.${NC}"
    read -p "Press Enter to continue or Ctrl+C to abort..."
fi

# Check if NVIDIA runtime is available
NVIDIA_AVAILABLE=false
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}NVIDIA GPU detected.${NC}"
    NVIDIA_AVAILABLE=true
    
    # Check if nvidia-docker is installed
    if docker info | grep -q "Runtimes:.*nvidia"; then
        echo -e "${GREEN}NVIDIA Docker runtime is available.${NC}"
    else
        echo -e "${YELLOW}NVIDIA Docker runtime not found. GPU acceleration will not be available.${NC}"
        echo -e "${YELLOW}To enable GPU acceleration, install the NVIDIA Container Toolkit:${NC}"
        echo -e "${YELLOW}https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html${NC}"
    fi
else
    echo -e "${YELLOW}No NVIDIA GPU detected. Running in CPU-only mode.${NC}"
    
    # Modify docker-compose.yml to remove NVIDIA service
    echo -e "${YELLOW}Removing NVIDIA service from docker-compose configuration...${NC}"
    sed -i.bak '/nvidia-runtime:/,/soulcore-network/d' docker-compose.yml || echo -e "${YELLOW}Failed to modify docker-compose.yml, continuing anyway${NC}"
fi

# Build and start containers
echo -e "${GREEN}Building and starting containers...${NC}"
docker-compose build
docker-compose up -d

# Show running containers
echo -e "${GREEN}Running containers:${NC}"
docker-compose ps

# Show logs
echo -e "${GREEN}Container logs (press Ctrl+C to exit logs):${NC}"
docker-compose logs -f

# Cleanup function
cleanup() {
    echo -e "${YELLOW}Stopping containers...${NC}"
    docker-compose down
    echo -e "${GREEN}Containers stopped.${NC}"
}

# Register cleanup function to run on script exit
trap cleanup EXIT
