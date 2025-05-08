#!/bin/bash
# SoulCoreHub Component Verification Script
# This script checks if all required components are present and properly linked

echo "🧠 SoulCoreHub Component Verification"
echo "===================================="

# Store the current directory
SOULCORE_DIR=$(pwd)
echo "📂 SoulCoreHub directory: $SOULCORE_DIR"

# Check if all required files exist
echo -e "\n📋 Checking core files..."
REQUIRED_FILES=(
  "gptsoul_soulconfig.py"
  "anima_autonomous.py"
  "anima_nlp_intent.py"
  "anima_model_router.py"
  "anima_memory_bridge.py"
  "anima_huggingface_connector.py"
  "huggingface_bridge.py"
)

MISSING_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file exists"
  else
    echo "❌ $file is missing"
    MISSING_FILES=$((MISSING_FILES+1))
  fi
done

# Check if all required directories exist
echo -e "\n📁 Checking directories..."
REQUIRED_DIRS=(
  "logs"
  "memory"
  "config"
)

MISSING_DIRS=0
for dir in "${REQUIRED_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    echo "✅ $dir directory exists"
  else
    echo "❌ $dir directory is missing"
    MISSING_DIRS=$((MISSING_DIRS+1))
  fi
done

# Check if configuration files exist
echo -e "\n⚙️ Checking configuration files..."
CONFIG_FILES=(
  "config/anima_intents.json"
  "config/anima_command_tree.json"
  "config/anima_models.json"
  "config/anima_routing_rules.json"
)

MISSING_CONFIGS=0
for file in "${CONFIG_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file exists"
  else
    echo "❌ $file is missing"
    MISSING_CONFIGS=$((MISSING_CONFIGS+1))
  fi
done

# Check if memory files exist
echo -e "\n💾 Checking memory files..."
MEMORY_FILES=(
  "memory/anima_memory.json"
  "memory/gptsoul_memory.json"
)

MISSING_MEMORY=0
for file in "${MEMORY_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file exists"
  else
    echo "❌ $file is missing"
    MISSING_MEMORY=$((MISSING_MEMORY+1))
  fi
done

# Check file permissions
echo -e "\n🔒 Checking file permissions..."
EXECUTABLE_FILES=(
  "gptsoul_soulconfig.py"
  "anima_autonomous.py"
  "anima_nlp_intent.py"
  "anima_model_router.py"
  "anima_memory_bridge.py"
)

PERMISSION_ISSUES=0
for file in "${EXECUTABLE_FILES[@]}"; do
  if [ -f "$file" ]; then
    if [ -x "$file" ]; then
      echo "✅ $file is executable"
    else
      echo "❌ $file is not executable"
      PERMISSION_ISSUES=$((PERMISSION_ISSUES+1))
    fi
  fi
done

# Make sure all files are executable
echo -e "\n🔧 Setting permissions for all Python files..."
chmod +x *.py 2>/dev/null
echo "✅ Permissions updated"

# Create necessary directories if missing
if [ $MISSING_DIRS -gt 0 ]; then
  echo -e "\n🔧 Creating missing directories..."
  mkdir -p logs memory config
  echo "✅ Directories created"
fi

# Check for symbolic links
echo -e "\n🔗 Checking symbolic links..."
if [ ! -L "gptsoul.py" ] && [ -f "gptsoul_soulconfig.py" ]; then
  echo "Creating symbolic link for gptsoul.py..."
  ln -sf "$SOULCORE_DIR/gptsoul_soulconfig.py" "$SOULCORE_DIR/gptsoul.py" 2>/dev/null
  echo "✅ Symbolic link created"
elif [ -L "gptsoul.py" ]; then
  echo "✅ gptsoul.py symbolic link exists"
else
  echo "❌ Could not create symbolic link for gptsoul.py"
fi

# Check Python imports
echo -e "\n📦 Checking Python imports..."
python3 -c "
try:
    import importlib
    modules = [
        'anima_nlp_intent',
        'anima_model_router',
        'anima_memory_bridge'
    ]
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f'✅ {module} can be imported')
        except ImportError as e:
            print(f'❌ {module} cannot be imported: {e}')
except Exception as e:
    print(f'Error checking imports: {e}')
" 2>/dev/null || echo "❌ Error running Python import check"

# Summary
echo -e "\n📊 Verification Summary:"
echo "===================================="
echo "Missing core files: $MISSING_FILES"
echo "Missing directories: $MISSING_DIRS"
echo "Missing config files: $MISSING_CONFIGS"
echo "Missing memory files: $MISSING_MEMORY"
echo "Permission issues: $PERMISSION_ISSUES"

# Overall status
if [ $MISSING_FILES -eq 0 ] && [ $MISSING_CONFIGS -eq 0 ] && [ $PERMISSION_ISSUES -eq 0 ]; then
  echo -e "\n✅ All critical components are present and properly configured!"
  echo "You can now run the following commands to start SoulCoreHub:"
  echo "  python3 gptsoul_soulconfig.py --activate"
  echo "  python3 anima_autonomous.py --mode reflective"
else
  echo -e "\n⚠️ Some components are missing or not properly configured."
  echo "Please address the issues above before running SoulCoreHub."
fi

echo -e "\nVerification complete!"
