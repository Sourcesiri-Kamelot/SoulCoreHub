#!/bin/bash
# pre_activation.sh
# Performs pre-activation checks and setup for SoulCoreHub

echo "=========================================="
echo "🧠 SoulCoreHub Pre-Activation Script"
echo "=========================================="

# Create necessary directories if they don't exist
echo "📁 Creating necessary directories..."
mkdir -p projects
mkdir -p logs
mkdir -p memory
mkdir -p templates
mkdir -p backups

# Set permissions for executable files
echo "🔒 Setting permissions for executable files..."
chmod +x anima_autonomous.py
chmod +x builder_mode.py
chmod +x anima_builder_cli.py
chmod +x maintain_permissions.sh
chmod +x pre_activation.sh

# Check for required Python packages
echo "📦 Checking for required Python packages..."
python3 -c "import sys; print('Python version:', sys.version)" || { echo "❌ Python 3 is required but not found"; exit 1; }

# Create backup of important files
echo "💾 Creating backups of important files..."
mkdir -p backups/$(date +%Y%m%d)
cp -f anima_autonomous.py backups/$(date +%Y%m%d)/ 2>/dev/null || echo "⚠️ Could not backup anima_autonomous.py"
cp -f builder_mode.py backups/$(date +%Y%m%d)/ 2>/dev/null || echo "⚠️ Could not backup builder_mode.py"

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️ .env file not found. Creating template..."
    echo "# Environment variables for SoulCoreHub" > .env
    echo "GITHUB_TOKEN=your-github-token-here" >> .env
    echo "⚠️ Please update the .env file with your actual credentials"
fi

# Create projects directory if it doesn't exist
if [ ! -d "projects" ]; then
    echo "📁 Creating projects directory..."
    mkdir -p projects
fi

echo "✅ Pre-activation checks complete!"
echo "✅ You can now run: python anima_autonomous.py"
echo "=========================================="
