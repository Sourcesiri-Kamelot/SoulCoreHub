#!/bin/bash
# maintain_permissions.sh
# Ensures all necessary files have executable permissions

echo "=========================================="
echo "🔒 SoulCoreHub Permission Maintenance"
echo "=========================================="

# Core Python scripts
echo "📄 Setting permissions for core Python scripts..."
find . -name "*.py" -type f -exec chmod +x {} \; 2>/dev/null
echo "✅ Core Python scripts permissions set"

# Shell scripts
echo "📄 Setting permissions for shell scripts..."
find . -name "*.sh" -type f -exec chmod +x {} \; 2>/dev/null
echo "✅ Shell scripts permissions set"

# Server files
echo "📄 Setting permissions for server files..."
chmod +x server.js 2>/dev/null
echo "✅ Server files permissions set"

# Specific critical files
echo "📄 Setting permissions for critical files..."
chmod +x anima_autonomous.py 2>/dev/null
chmod +x builder_mode.py 2>/dev/null
chmod +x anima_builder_cli.py 2>/dev/null
chmod +x pre_activation.sh 2>/dev/null
chmod +x maintain_permissions.sh 2>/dev/null
echo "✅ Critical files permissions set"

# Secure sensitive files
echo "🔒 Securing sensitive files..."
chmod 700 .env 2>/dev/null
echo "✅ Sensitive files secured"

echo "✅ All permissions have been set!"
echo "=========================================="
