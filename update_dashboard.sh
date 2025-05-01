#!/bin/bash

# Update SoulCore Dashboard
echo "Updating SoulCore Dashboard..."

# Update all Python scripts to use python3
echo "Updating soulcore_dashboard_fixed.html to use python3..."
sed -i '' 's/python /python3 /g' soulcore_dashboard_fixed.html

# Backup the original dashboard
cp soulcore_dashboard.html soulcore_dashboard.html.bak

# Replace with the fixed version
cp soulcore_dashboard_fixed.html soulcore_dashboard.html

# Restart the dashboard server
pkill -f "node soulcore_dashboard_server.js"
bash start_dashboard.sh

echo "Dashboard updated and restarted!"
echo "Access the dashboard at http://localhost:3000"
