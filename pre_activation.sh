#!/bin/bash
# pre_activation.sh - Script to run before full SoulCoreHub activation

echo "Running pre-activation checks for SoulCoreHub..."

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
  echo "Virtual environment not activated. Activating now..."
  source /Users/helo.im.ai/SoulCoreHub/myenv/bin/activate
fi

# Maintain permissions
echo "Setting executable permissions..."
bash /Users/helo.im.ai/SoulCoreHub/maintain_permissions.sh

# Check for required dependencies
echo "Checking dependencies..."
pip list | grep -E "numpy|tensorflow|requests|flask" || {
  echo "Some dependencies may be missing. Installing from requirements.txt..."
  pip install -r /Users/helo.im.ai/SoulCoreHub/requirements.txt
}

# Check system resources
echo "Checking system resources..."
free_memory=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
if [[ $free_memory -lt 1000 ]]; then
  echo "WARNING: System memory is low. Consider closing other applications before activation."
fi

echo "Pre-activation checks complete. Ready for SoulCoreHub activation."
echo "To start the system, run: python anima_autonomous.py"
