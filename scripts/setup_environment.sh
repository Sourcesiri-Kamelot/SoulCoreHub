#!/bin/bash
# SoulCoreHub Environment Setup Script
# This script sets up the development environment for SoulCoreHub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  SoulCoreHub Environment Setup  ${NC}"
echo -e "${GREEN}=========================================${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}pip3 is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is not installed. Please install it first.${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip3 install -r requirements.txt

# Install Node.js dependencies
echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
npm install

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p data/commerce
mkdir -p data/content
mkdir -p data/culture/worlds
mkdir -p data/culture/docs
mkdir -p logs
mkdir -p config/agents

# Create sample .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating sample .env file...${NC}"
    cat > .env << EOL
# SoulCoreHub Environment Variables
# Replace these values with your actual credentials

# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_ACCOUNT_ID=your_account_id
AWS_REGION=us-east-1

# Email Configuration
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
EMAIL_FROM=noreply@example.com
EMAIL_REPLY_TO=support@example.com

# API Keys
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key

# Development Settings
DEBUG=true
LOG_LEVEL=info
EOL
    echo -e "${GREEN}Sample .env file created. Please update it with your actual credentials.${NC}"
else
    echo -e "${YELLOW}.env file already exists. Skipping creation.${NC}"
fi

# Create sample agent configuration files
echo -e "${YELLOW}Creating sample agent configuration files...${NC}"
for AGENT in "gptsoul" "anima" "evove" "azur"; do
    CONFIG_FILE="config/agents/${AGENT}_config.json"
    if [ ! -f "$CONFIG_FILE" ]; then
        cat > "$CONFIG_FILE" << EOL
{
    "agent_name": "${AGENT^}",
    "description": "Ethical AI agent for SoulCoreHub: ${AGENT^}",
    "version": "1.0.0",
    "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "ethical_level": "high",
    "transparency": "full",
    "capabilities": [
        "text_generation",
        "content_analysis",
        "ethical_decision_making"
    ],
    "limitations": [
        "No access to sensitive user data without consent",
        "No autonomous financial transactions",
        "No deceptive or manipulative behavior"
    ],
    "allowed_actions": [
        "generate_content",
        "analyze_content",
        "provide_recommendations",
        "log_activity"
    ]
}
EOL
        echo -e "${GREEN}Created configuration for ${AGENT^} agent.${NC}"
    else
        echo -e "${YELLOW}Configuration for ${AGENT^} agent already exists. Skipping creation.${NC}"
    fi
done

# Create requirements.txt if it doesn't exist
if [ ! -f requirements.txt ]; then
    echo -e "${YELLOW}Creating requirements.txt file...${NC}"
    cat > requirements.txt << EOL
# Core dependencies
boto3>=1.26.0
python-dotenv>=1.0.0
requests>=2.28.0
pandas>=1.5.0
numpy>=1.23.0

# AWS integration
awscli>=1.27.0

# Security
cryptography>=39.0.0

# Web framework
flask>=2.2.0
flask-cors>=3.0.10

# Database
pymongo>=4.3.0

# Utilities
pyyaml>=6.0
tqdm>=4.64.0
EOL
    echo -e "${GREEN}requirements.txt file created.${NC}"
else
    echo -e "${YELLOW}requirements.txt file already exists. Skipping creation.${NC}"
fi

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo -e "${YELLOW}Creating .gitignore file...${NC}"
    cat > .gitignore << EOL
# Environment variables
.env
.env.*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Node.js
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log
package-lock.json

# Logs
logs/
*.log

# Data
data/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOL
    echo -e "${GREEN}.gitignore file created.${NC}"
else
    echo -e "${YELLOW}.gitignore file already exists. Skipping creation.${NC}"
fi

# Set executable permissions for scripts
echo -e "${YELLOW}Setting executable permissions for scripts...${NC}"
chmod +x scripts/*.sh

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Environment Setup Complete!  ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Update the .env file with your actual credentials"
echo -e "2. Run 'source venv/bin/activate' to activate the virtual environment"
echo -e "3. Run 'python -m src.agents.ethical_agent_framework' to test the framework"
echo -e ""
