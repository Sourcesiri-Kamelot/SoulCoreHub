#!/bin/bash

# Install Scheduler Components for SoulCoreHub
# This script installs and configures the skill scheduling system

echo "🔄 Installing Anima Skill Scheduler..."

# Install required packages
pip install apscheduler

# Create logs directory if it doesn't exist
mkdir -p logs

# Make the script executable
chmod +x "$0"

# Copy the scheduler files to the correct locations
echo "📂 Installing scheduler files..."

# Make scheduler.py executable
chmod +x scheduler.py
chmod +x anima_skill_scheduler.py
chmod +x soulcorehub_server_scheduler.py

# Create a symbolic link to the new server
echo "🔗 Creating server link..."
mv soulcorehub_server.py soulcorehub_server.py.bak
ln -sf soulcorehub_server_scheduler.py soulcorehub_server.py

# Update the maintain_permissions.sh script to include the scheduler files
echo "🔒 Updating permissions script..."
if [ -f maintain_permissions.sh ]; then
    if ! grep -q "scheduler.py" maintain_permissions.sh; then
        sed -i '' '/# Make Python files executable/a\\
chmod +x scheduler.py anima_skill_scheduler.py soulcorehub_server_scheduler.py' maintain_permissions.sh
    fi
fi

# Create a startup script for the scheduler
echo "🚀 Creating startup script..."
cat > start_scheduler.sh << 'EOF'
#!/bin/bash

# Start the SoulCoreHub server with scheduler
echo "🚀 Starting SoulCoreHub server with scheduler..."
python soulcorehub_server.py &
SERVER_PID=$!

# Wait for the server to start
sleep 2

# Open the dashboard in the default browser
echo "🌐 Opening dashboard..."
open http://localhost:5000/scheduled-skills

# Wait for user to press Ctrl+C
echo "⏱️ Server running. Press Ctrl+C to stop."
trap "kill $SERVER_PID; echo '🛑 Server stopped.'; exit 0" INT
wait
EOF

chmod +x start_scheduler.sh

echo "✅ Anima Skill Scheduler installed successfully!"
echo "🚀 Run './start_scheduler.sh' to start the server with scheduling capabilities."
