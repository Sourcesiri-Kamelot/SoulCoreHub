#!/bin/bash
# EvoVe's MCP Health Check Script
# This script checks the health of the MCP system and repairs it if necessary

# Configuration
MCP_HOST="localhost"
MCP_PORT=8765
MAX_RETRIES=3
TIMEOUT=5
LOG_FILE="logs/mcp_health.log"

# Ensure log directory exists
mkdir -p $(dirname "$LOG_FILE")

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting MCP health check"

# Check if MCP server is running
check_mcp() {
    log "Checking MCP server at $MCP_HOST:$MCP_PORT"
    
    # Try to connect to the MCP server
    if nc -z -w$TIMEOUT $MCP_HOST $MCP_PORT 2>/dev/null; then
        log "MCP server is running"
        return 0
    else
        log "MCP server is not responding"
        return 1
    fi
}

# Find the MCP server script
find_mcp_script() {
    local script_paths=(
        "mcp/mcp_server_divine.py"
        "mcp_server_divine.py"
        "../mcp/mcp_server_divine.py"
    )
    
    for path in "${script_paths[@]}"; do
        if [ -f "$path" ]; then
            echo "$path"
            return 0
        fi
    done
    
    log "Could not find MCP server script"
    return 1
}

# Restart the MCP server
restart_mcp() {
    log "Attempting to restart MCP server"
    
    # Find the MCP script
    local mcp_script=$(find_mcp_script)
    if [ $? -ne 0 ]; then
        log "Failed to find MCP server script"
        return 1
    fi
    
    log "Found MCP script at $mcp_script"
    
    # Check if MCP is already running as a process
    local mcp_pid=$(pgrep -f "python.*$mcp_script" || true)
    if [ -n "$mcp_pid" ]; then
        log "MCP server is already running with PID $mcp_pid, killing it"
        kill $mcp_pid
        sleep 2
        
        # Check if it's still running
        if ps -p $mcp_pid > /dev/null; then
            log "MCP server did not shut down gracefully, forcing kill"
            kill -9 $mcp_pid
            sleep 1
        fi
    fi
    
    # Start the MCP server
    log "Starting MCP server"
    python "$mcp_script" > "logs/mcp_server.log" 2>&1 &
    
    # Wait for server to start
    sleep 3
    
    # Check if server started successfully
    if check_mcp; then
        log "MCP server restarted successfully"
        return 0
    else
        log "Failed to restart MCP server"
        return 1
    fi
}

# Create a backup
create_backup() {
    local timestamp=$(date '+%Y%m%d-%H%M%S')
    local backup_dir="backups"
    local backup_file="$backup_dir/mcp-backup-$timestamp.tar.gz"
    
    log "Creating backup at $backup_file"
    
    # Ensure backup directory exists
    mkdir -p "$backup_dir"
    
    # Create backup
    tar -czf "$backup_file" mcp/ config/ *.py 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "Backup created successfully"
        return 0
    else
        log "Failed to create backup"
        return 1
    fi
}

# Main execution
if check_mcp; then
    log "MCP health check passed"
    exit 0
else
    log "MCP health check failed"
    
    # Create backup before repair
    create_backup
    
    # Try to restart MCP
    for ((i=1; i<=MAX_RETRIES; i++)); do
        log "Repair attempt $i of $MAX_RETRIES"
        if restart_mcp; then
            log "MCP repair successful"
            exit 0
        fi
        sleep 2
    done
    
    log "All repair attempts failed"
    
    # Notify EvoVe about the failure
    if [ -f "evove_autonomous.py" ]; then
        log "Notifying EvoVe about the failure"
        python evove_autonomous.py --repair
    fi
    
    exit 1
fi


