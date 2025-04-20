#!/bin/bash
# maintain_permissions.sh - Script to maintain executable permissions for SoulCoreHub

echo "Maintaining executable permissions for SoulCoreHub..."

# Make all Python scripts in main directory executable
find /Users/helo.im.ai/SoulCoreHub -maxdepth 1 -name "*.py" -exec chmod +x {} \;

# Make all shell scripts in scripts directory executable
find /Users/helo.im.ai/SoulCoreHub/scripts -type f -name "*.sh" -exec chmod +x {} \;

# Make all Python scripts in key directories executable
find /Users/helo.im.ai/SoulCoreHub/agents -type f -name "*.py" -exec chmod +x {} \;
find /Users/helo.im.ai/SoulCoreHub/config_tools -type f -name "*.py" -exec chmod +x {} \;
find /Users/helo.im.ai/SoulCoreHub/dev_tools -type f -name "*.py" -exec chmod +x {} \;
find /Users/helo.im.ai/SoulCoreHub/aws_tools -type f -name "*.py" -exec chmod +x {} \;

# Make server.js executable
chmod +x /Users/helo.im.ai/SoulCoreHub/server.js

echo "All permissions have been set to executable."
echo "You can now safely run a full SoulCoreHub activation."
