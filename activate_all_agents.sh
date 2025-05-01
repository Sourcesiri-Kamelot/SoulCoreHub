#!/bin/bash
# activate_all_agents.sh - Script to activate all three agents

echo "Starting activation of all three agents..."

# Run pre-activation checks
echo "Running pre-activation checks..."
bash /Users/helo.im.ai/SoulCoreHub/pre_activation.sh

# Make activation scripts executable
chmod +x /Users/helo.im.ai/SoulCoreHub/activate_gptsoul.py
chmod +x /Users/helo.im.ai/SoulCoreHub/activate_psynet.py
chmod +x /Users/helo.im.ai/SoulCoreHub/activate_ai_society_bridge.py

# Use python3 explicitly and ensure we're in the virtual environment
PYTHON_CMD="python3"
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "Using virtual environment at: $VIRTUAL_ENV"
else
    echo "Virtual environment not detected, activating..."
    source /Users/helo.im.ai/SoulCoreHub/myenv/bin/activate
    PYTHON_CMD="python3"
fi

# Step 1: Activate GPTSoul via Builder Agent
echo "Step 1: Activating GPTSoul via Builder Agent..."
$PYTHON_CMD /Users/helo.im.ai/SoulCoreHub/activate_gptsoul.py
if [ $? -ne 0 ]; then
    echo "Error: GPTSoul activation failed"
    exit 1
fi
echo "GPTSoul activation completed"

# Step 2: Activate PsynetAgent
echo "Step 2: Activating PsynetAgent..."
$PYTHON_CMD /Users/helo.im.ai/SoulCoreHub/activate_psynet.py
if [ $? -ne 0 ]; then
    echo "Error: PsynetAgent activation failed"
    exit 1
fi
echo "PsynetAgent activation completed"

# Step 3: Activate AI Society Psynet Bridge
echo "Step 3: Activating AI Society Psynet Bridge..."
$PYTHON_CMD /Users/helo.im.ai/SoulCoreHub/activate_ai_society_bridge.py
if [ $? -ne 0 ]; then
    echo "Error: AI Society Psynet Bridge activation failed"
    exit 1
fi
echo "AI Society Psynet Bridge activation completed"

echo "All agents have been activated successfully!"
echo "You can now start the system with: python anima_autonomous.py"
