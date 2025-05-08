#!/bin/bash
# SoulCoreHub SAM Script Runner
# This script provides a unified interface for running AWS SAM commands within SoulCore

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Display SoulCore banner
echo -e "${BLUE}"
echo "🧠 SoulCoreHub SAM Script Runner"
echo "==============================="
echo -e "${NC}"

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ AWS SAM CLI is not installed. Please install it first.${NC}"
    echo "   Visit: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html"
    exit 1
fi

# Function to display help
show_help() {
    echo -e "${YELLOW}Usage:${NC} $0 [command] [options]"
    echo ""
    echo -e "${YELLOW}Available commands:${NC}"
    echo "  init        - Initialize a new SAM application"
    echo "  build       - Build the SAM application"
    echo "  deploy      - Deploy the SAM application to AWS"
    echo "  local       - Run the application locally"
    echo "  logs        - View Lambda function logs"
    echo "  validate    - Validate the SAM template"
    echo "  stripe      - Add Stripe usage record"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 init     - Initialize a new SAM application"
    echo "  $0 build    - Build the current SAM application"
    echo "  $0 deploy   - Deploy the application to AWS"
    echo "  $0 local    - Run the application locally"
    echo "  $0 logs function-name - View logs for a specific function"
    echo "  $0 stripe user_id=123 units=5 - Record 5 units of usage for user 123"
}

# Function to initialize a new SAM application
run_init() {
    echo -e "${GREEN}Initializing new SAM application...${NC}"
    sam init
}

# Function to build the SAM application
run_build() {
    echo -e "${GREEN}Building SAM application...${NC}"
    ./sam_build.sh
}

# Function to deploy the SAM application
run_deploy() {
    echo -e "${GREEN}Deploying SAM application...${NC}"
    ./sam_deploy.sh
}

# Function to run the application locally
run_local() {
    echo -e "${GREEN}Running application locally...${NC}"
    ./sam_local_test.sh
}

# Function to view Lambda function logs
run_logs() {
    if [ -z "$2" ]; then
        echo -e "${RED}❌ Function name is required.${NC}"
        echo "Usage: $0 logs function-name"
        exit 1
    fi
    
    echo -e "${GREEN}Fetching logs for function: $2...${NC}"
    sam logs -n "$2" --stack-name soulcore-hub --tail
}

# Function to validate the SAM template
run_validate() {
    echo -e "${GREEN}Validating SAM template...${NC}"
    sam validate
}

# Function to add Stripe usage record
run_stripe() {
    # Parse arguments
    user_id=""
    units=0
    reason=""
    
    for arg in "$@"; do
        if [[ $arg == user_id=* ]]; then
            user_id="${arg#*=}"
        elif [[ $arg == units=* ]]; then
            units="${arg#*=}"
        elif [[ $arg == reason=* ]]; then
            reason="${arg#*=}"
        fi
    done
    
    # Validate required parameters
    if [ -z "$user_id" ] || [ -z "$units" ]; then
        echo -e "${RED}❌ Both user_id and units are required.${NC}"
        echo "Usage: $0 stripe user_id=123 units=5 [reason=api_call]"
        exit 1
    fi
    
    echo -e "${GREEN}Recording Stripe usage: $units units for user $user_id${NC}"
    if [ -n "$reason" ]; then
        echo -e "${GREEN}Reason: $reason${NC}"
    fi
    
    # Invoke the Lambda function to record usage
    aws lambda invoke \
        --function-name soulcore-hub-StripeBillingLambda \
        --payload "{\"user_id\":\"$user_id\",\"units\":$units,\"reason\":\"$reason\"}" \
        --cli-binary-format raw-in-base64-out \
        /tmp/stripe_response.json
        
    # Check if the invocation was successful
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Usage record added successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to add usage record. Check AWS Lambda logs for details.${NC}"
    fi
}

# Main command router
case "$1" in
    init)
        run_init
        ;;
    build)
        run_build
        ;;
    deploy)
        run_deploy
        ;;
    local)
        run_local
        ;;
    logs)
        run_logs "$@"
        ;;
    validate)
        run_validate
        ;;
    stripe)
        shift
        run_stripe "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac

exit 0
