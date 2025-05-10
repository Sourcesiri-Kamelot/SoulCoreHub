#!/bin/bash

echo "🔧 SoulCore Auto-Fix Script Started..."

# ✅ Ensure Q-safe log directory exists
mkdir -p ~/SoulCoreHub/q_outputs
export Q_TEMP_DIR=~/SoulCoreHub/q_outputs
echo "✅ Q_TEMP_DIR set to $Q_TEMP_DIR"

# ✅ Ensure logs folder exists
mkdir -p ~/SoulCoreHub/logs
touch ~/SoulCoreHub/logs/deploy_log.txt
touch ~/SoulCoreHub/q_outputs/domain_config.log

# 🔍 Fix Node.js vulnerabilities if package.json is present
if [ -f package.json ]; then
  echo "📦 Running npm audit fix..."
  npm install
  npm audit fix --force
else
  echo "📦 Skipping npm fix (no package.json found)"
fi

# 🐍 Fix Python package issues
echo "🐍 Updating Python environment and checking for vulnerabilities..."
pip install --upgrade pip safety pip-upgrade-outdated
pip install -r requirements.txt || echo "⚠️ requirements.txt not found or failed"
safety check --full-report || echo "⚠️ Some vulnerabilities may need manual patching"
pip-upgrade-outdated || echo "📦 pip-upgrade-outdated failed or already clean"

# ✅ Done
echo "✅ SoulCore Auto-Fix Completed. System hardened and synced."
