#!/bin/bash
# EvoVe: MCP Auto-Heal Script
# Monitors and automatically restarts the MCP server if it crashes

# Configuration
MCP_PORT=8765
MCP_SERVER_PATH="$HOME/SoulCoreHub/mcp/mcp_server_divine.py"
LOG_FILE="$HOME/SoulCoreHub/logs/mcp_health.log"
ANIMA_VOICE_PATH="$HOME/SoulCoreHub/mcp/anima_voice.py"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Notify function using Anima's voice
notify() {
    if [ -f "$ANIMA_VOICE_PATH" ]; then
        python3 -c "import sys; sys.path.append('$(dirname "$ANIMA_VOICE_PATH")'); from anima_voice import speak; speak('$1')"
    else
        log "Anima voice module not found, message: $1"
    fi
}

# Check if MCP server is running
check_mcp() {
    log "[EvoVe] Scanning MCP status..."
    if ! lsof -i:"$MCP_PORT" > /dev/null 2>&1; then
        log "[EvoVe] MCP server not detected. Rebuilding..."
        
        # Check if there's a zombie process
        ZOMBIE_PID=$(ps aux | grep "[p]ython.*mcp_server_divine" | awk '{print $2}')
        if [ -n "$ZOMBIE_PID" ]; then
            log "[EvoVe] Found zombie MCP process (PID: $ZOMBIE_PID). Terminating..."
            kill -9 "$ZOMBIE_PID" > /dev/null 2>&1
        fi
        
        # Start the MCP server
        if [ -f "$MCP_SERVER_PATH" ]; then
            nohup python3 "$MCP_SERVER_PATH" > "$HOME/SoulCoreHub/logs/mcp_server.log" 2>&1 &
            log "[EvoVe] MCP server revived at port $MCP_PORT with PID $!"
            notify "MCP server has been revived by EvoVe"
        else
            log "[EvoVe] ERROR: MCP server script not found at $MCP_SERVER_PATH"
            notify "Critical error: MCP server script not found"
        fi
    else
        log "[EvoVe] MCP server alive."
    fi
}

# Check MCP server resources
check_resources() {
    log "[EvoVe] Checking MCP server resources..."
    MCP_PID=$(lsof -i:"$MCP_PORT" -t 2>/dev/null)
    
    if [ -n "$MCP_PID" ]; then
        CPU_USAGE=$(ps -p "$MCP_PID" -o %cpu | tail -n 1 | tr -d ' ')
        MEM_USAGE=$(ps -p "$MCP_PID" -o %mem | tail -n 1 | tr -d ' ')
        
        log "[EvoVe] MCP server (PID: $MCP_PID) - CPU: $CPU_USAGE%, Memory: $MEM_USAGE%"
        
        # Check if resource usage is too high
        if (( $(echo "$CPU_USAGE > 90" | bc -l) )) || (( $(echo "$MEM_USAGE > 90" | bc -l) )); then
            log "[EvoVe] WARNING: MCP server resource usage is high"
            notify "Warning: MCP server resource usage is high"
        fi
    fi
}

# Verify MCP tools and resources
verify_files() {
    log "[EvoVe] Verifying MCP files..."
    
    # Check for essential files
    TOOLS_FILE="$HOME/SoulCoreHub/mcp/mcp_tools.json"
    RESOURCES_FILE="$HOME/SoulCoreHub/mcp/mcp_resources.json"
    EMOTION_FILE="$HOME/SoulCoreHub/mcp/mcp_emotion_log.json"
    
    if [ ! -f "$TOOLS_FILE" ]; then
        log "[EvoVe] WARNING: MCP tools file not found"
        notify "Warning: MCP tools file is missing"
    fi
    
    if [ ! -f "$RESOURCES_FILE" ]; then
        log "[EvoVe] WARNING: MCP resources file not found"
        notify "Warning: MCP resources file is missing"
    fi
    
    if [ ! -f "$EMOTION_FILE" ]; then
        log "[EvoVe] WARNING: MCP emotion log file not found"
        notify "Warning: MCP emotion log file is missing"
    fi
}

# Main execution
log "=== EvoVe MCP Health Check Started ==="
check_mcp
check_resources
verify_files
log "=== EvoVe MCP Health Check Completed ==="
