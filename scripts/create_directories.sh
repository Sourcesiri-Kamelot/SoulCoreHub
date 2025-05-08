#!/bin/bash
# Create necessary directories for the SAM integration

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "🧠 SoulCoreHub Directory Setup"
echo "============================="
echo -e "${NC}"

# Create directories if they don't exist
mkdir -p functions/anima
mkdir -p functions/gptsoul
mkdir -p functions/neural_router
mkdir -p functions/memory_sync
mkdir -p functions/resurrection
mkdir -p functions/dashboard
mkdir -p functions/auth
mkdir -p functions/payment
mkdir -p functions/stripe_billing
mkdir -p anima_commands
mkdir -p logs

echo -e "${GREEN}✅ Created necessary directories for SAM integration${NC}"

# Create placeholder files in empty directories
for dir in functions/anima functions/gptsoul functions/neural_router functions/memory_sync functions/resurrection functions/dashboard functions/auth functions/payment; do
    if [ ! -f "$dir/app.py" ]; then
        echo "# Placeholder file for $dir" > "$dir/app.py"
        echo "# Add your code here" >> "$dir/app.py"
        echo -e "${YELLOW}Created placeholder app.py in $dir${NC}"
    fi
    
    if [ ! -f "$dir/requirements.txt" ]; then
        echo "boto3==1.28.38" > "$dir/requirements.txt"
        echo -e "${YELLOW}Created placeholder requirements.txt in $dir${NC}"
    fi
done

echo -e "${GREEN}✅ Setup complete!${NC}"
