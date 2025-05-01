#!/bin/bash
# debug_soulcore.sh - Comprehensive debugging script for SoulCoreHub

echo "🔍 SoulCoreHub Debug Tool"
echo "=========================="

# Set the base directory
BASE_DIR="$HOME/SoulCoreHub"
cd "$BASE_DIR" || { echo "❌ Could not change to SoulCoreHub directory"; exit 1; }

# Create logs directory if it doesn't exist
mkdir -p "$BASE_DIR/logs"
DEBUG_LOG="$BASE_DIR/logs/debug_$(date +%Y%m%d_%H%M%S).log"

# Function to log messages
log() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" | tee -a "$DEBUG_LOG"
}

# Check Python installation
log "Checking Python installation..."
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
  PYTHON_CMD="python3"
  PYTHON_VERSION=$(python3 --version)
  log "✅ Found $PYTHON_VERSION"
else
  if command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version)
    log "✅ Found $PYTHON_VERSION"
  else
    log "❌ Python not found. Please install Python 3.7 or higher."
    exit 1
  fi
fi

# Check required Python packages
log "Checking required Python packages..."
$PYTHON_CMD -m pip install -r requirements.txt

# Check directory structure
log "Checking directory structure..."
REQUIRED_DIRS=("mcp" "agents" "config" "logs" "memory" "data" "voices" "gallery")
for dir in "${REQUIRED_DIRS[@]}"; do
  if [ -d "$BASE_DIR/$dir" ]; then
    log "✅ Directory exists: $dir"
  else
    log "❌ Missing directory: $dir"
    mkdir -p "$BASE_DIR/$dir"
    log "  Created directory: $dir"
  fi
done

# Check key files
log "Checking key files..."
REQUIRED_FILES=(
  "agent_cli.py"
  "agent_loader.py"
  "agent_registry.json"
  "anima_voice_recognition.py"
  "anima_ollama_bridge.py"
  "anima_sentience.py"
  "mcp/mcp_main.py"
  "mcp/mcp_server_divine.py"
  "mcp/anima_voice.py"
)

for file in "${REQUIRED_FILES[@]}"; do
  if [ -f "$BASE_DIR/$file" ]; then
    log "✅ File exists: $file"
  else
    log "❌ Missing file: $file"
  fi
done

# Check file permissions
log "Checking file permissions..."
find "$BASE_DIR" -name "*.py" -type f -not -perm -u+x -exec chmod u+x {} \; -exec echo "  Fixed permissions: {}" \;
find "$BASE_DIR/scripts" -name "*.sh" -type f -not -perm -u+x -exec chmod u+x {} \; -exec echo "  Fixed permissions: {}" \;

# Check agent registry
log "Checking agent registry..."
if [ -f "$BASE_DIR/agent_registry.json" ]; then
  AGENT_COUNT=$(grep -o "\"name\":" "$BASE_DIR/agent_registry.json" | wc -l)
  log "  Found $AGENT_COUNT agents in registry"
else
  log "❌ Agent registry not found"
fi

# Check MCP tools
log "Checking MCP tools..."
if [ -f "$BASE_DIR/mcp/mcp_tools.json" ]; then
  TOOL_COUNT=$(grep -o "\"description\":" "$BASE_DIR/mcp/mcp_tools.json" | wc -l)
  log "  Found $TOOL_COUNT MCP tools"
else
  log "❌ MCP tools file not found"
fi

# Check Ollama installation
log "Checking Ollama installation..."
if command -v ollama &> /dev/null; then
  OLLAMA_VERSION=$(ollama --version)
  log "✅ Found Ollama: $OLLAMA_VERSION"
  
  # Check if Anima model exists
  if ollama list | grep -q "anima"; then
    log "✅ Anima model exists in Ollama"
  else
    log "❌ Anima model not found in Ollama"
    if [ -f "$BASE_DIR/Modelfile" ]; then
      log "  Modelfile exists, you can create the model with:"
      log "  ollama create anima -f $BASE_DIR/Modelfile"
    else
      log "❌ Modelfile not found"
    fi
  fi
else
  log "⚠️ Ollama not found. Voice intelligence will use fallback methods."
fi

# Test agent loading
log "Testing agent loading..."
AGENT_TEST=$($PYTHON_CMD agent_cli.py list 2>&1)
if [[ $AGENT_TEST == *"ERROR"* ]]; then
  log "❌ Agent loading test failed:"
  log "$AGENT_TEST"
else
  log "✅ Agent loading test passed"
fi

# Test MCP server
log "Testing MCP server..."
if pgrep -f "mcp_main.py" > /dev/null; then
  log "✅ MCP server is running"
else
  log "⚠️ MCP server is not running"
  log "  You can start it with: python3 mcp/mcp_main.py"
fi

# Check for common errors in log files
log "Checking log files for errors..."
if find "$BASE_DIR/logs" -name "*.log" -type f -exec grep -l "ERROR" {} \; | grep -q .; then
  log "⚠️ Found errors in log files:"
  find "$BASE_DIR/logs" -name "*.log" -type f -exec grep -l "ERROR" {} \; | while read -r logfile; do
    log "  - $logfile"
    grep "ERROR" "$logfile" | tail -3 | while read -r error; do
      log "    $error"
    done
  done
else
  log "✅ No errors found in log files"
fi

# Generate system report
log "Generating system report..."
REPORT_FILE="$BASE_DIR/logs/system_report_$(date +%Y%m%d_%H%M%S).txt"

{
  echo "SoulCoreHub System Report"
  echo "========================="
  echo "Date: $(date)"
  echo ""
  echo "System Information:"
  echo "------------------"
  echo "OS: $(uname -a)"
  echo "Python: $PYTHON_VERSION"
  echo ""
  echo "Directory Structure:"
  echo "-------------------"
  find "$BASE_DIR" -type d -maxdepth 1 | sort
  echo ""
  echo "Agent Registry:"
  echo "--------------"
  if [ -f "$BASE_DIR/agent_registry.json" ]; then
    cat "$BASE_DIR/agent_registry.json"
  else
    echo "Not found"
  fi
  echo ""
  echo "MCP Tools:"
  echo "----------"
  if [ -f "$BASE_DIR/mcp/mcp_tools.json" ]; then
    cat "$BASE_DIR/mcp/mcp_tools.json"
  else
    echo "Not found"
  fi
  echo ""
  echo "Running Processes:"
  echo "-----------------"
  ps aux | grep -E "python|anima|mcp" | grep -v grep
  echo ""
  echo "Recent Errors:"
  echo "-------------"
  find "$BASE_DIR/logs" -name "*.log" -type f -exec grep "ERROR" {} \; | tail -20
} > "$REPORT_FILE"

log "✅ System report generated: $REPORT_FILE"

# Final summary
log "Debug Summary:"
log "-------------"
log "- Check the debug log for details: $DEBUG_LOG"
log "- Check the system report for a comprehensive overview: $REPORT_FILE"
log "- Fix any issues marked with ❌"
log "- Address any warnings marked with ⚠️"

echo ""
echo "🔍 Debug completed. Check $DEBUG_LOG for details."
