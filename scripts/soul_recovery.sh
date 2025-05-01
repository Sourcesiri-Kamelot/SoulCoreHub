#!/bin/bash
# soul_recovery.sh - Emergency recovery script for SoulCore system

# Set the base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR" || exit 1

# Create logs directory
mkdir -p "$BASE_DIR/logs"

# Log file for recovery operations
RECOVERY_LOG="$BASE_DIR/logs/recovery_$(date +%Y%m%d_%H%M%S).log"

# Function to log messages
log_message() {
    local message="$1"
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $message" | tee -a "$RECOVERY_LOG"
}

# Function to stop all SoulCore processes
stop_all_processes() {
    log_message "Stopping all SoulCore processes..."
    
    # Stop MCP server
    pkill -f "python.*mcp_main.py" 2>/dev/null
    
    # Stop Anima
    pkill -f "python.*anima_" 2>/dev/null
    
    # Stop EvoVe
    pkill -f "python.*evove_" 2>/dev/null
    
    # Stop web server
    pkill -f "node.*server.js" 2>/dev/null
    
    # Wait for processes to stop
    sleep 2
    
    log_message "All processes stopped"
}

# Function to repair file permissions
repair_permissions() {
    log_message "Repairing file permissions..."
    
    # Make maintain_permissions.sh executable
    chmod +x "$BASE_DIR/maintain_permissions.sh" 2>/dev/null
    
    # Run maintain_permissions.sh if it exists
    if [ -f "$BASE_DIR/maintain_permissions.sh" ]; then
        bash "$BASE_DIR/maintain_permissions.sh" >> "$RECOVERY_LOG" 2>&1
    else
        # Manual permission repair
        find "$BASE_DIR" -name "*.py" -exec chmod +x {} \; 2>/dev/null
        find "$BASE_DIR/scripts" -name "*.sh" -exec chmod +x {} \; 2>/dev/null
        chmod +x "$BASE_DIR/server.js" 2>/dev/null
    fi
    
    log_message "File permissions repaired"
}

# Function to create essential directories
create_directories() {
    log_message "Creating essential directories..."
    
    mkdir -p "$BASE_DIR/mcp"
    mkdir -p "$BASE_DIR/scripts"
    mkdir -p "$BASE_DIR/logs"
    mkdir -p "$BASE_DIR/data"
    mkdir -p "$BASE_DIR/modules"
    mkdir -p "$BASE_DIR/evove"
    mkdir -p "$BASE_DIR/anima"
    mkdir -p "$BASE_DIR/voices"
    mkdir -p "$BASE_DIR/gallery"
    
    log_message "Essential directories created"
}

# Function to start the MCP server
start_mcp_server() {
    log_message "Starting MCP server..."
    
    if [ -f "$BASE_DIR/mcp/mcp_main.py" ]; then
        cd "$BASE_DIR/mcp" && python mcp_main.py > "$BASE_DIR/logs/mcp_server.log" 2>&1 &
        sleep 2
        
        if pgrep -f "python.*mcp_main.py" > /dev/null; then
            log_message "MCP server started successfully"
            return 0
        else
            log_message "Failed to start MCP server"
            return 1
        fi
    else
        log_message "MCP main file not found"
        return 1
    fi
}

# Function to start EvoVe
start_evove() {
    log_message "Starting EvoVe..."
    
    if [ -f "$BASE_DIR/scripts/start_evove.sh" ]; then
        bash "$BASE_DIR/scripts/start_evove.sh" >> "$RECOVERY_LOG" 2>&1
        
        if pgrep -f "python.*evove_autonomous.py" > /dev/null; then
            log_message "EvoVe started successfully"
            return 0
        else
            log_message "Failed to start EvoVe"
            return 1
        fi
    else
        log_message "EvoVe start script not found"
        return 1
    fi
}

# Main recovery process
log_message "Starting SoulCore emergency recovery process"

# Stop all processes
stop_all_processes

# Create essential directories
create_directories

# Repair file permissions
repair_permissions

# Start MCP server
start_mcp_server
mcp_status=$?

# Start EvoVe if MCP server started successfully
if [ $mcp_status -eq 0 ]; then
    start_evove
    evove_status=$?
    
    if [ $evove_status -eq 0 ]; then
        log_message "Recovery process completed successfully"
    else
        log_message "Recovery process completed with warnings (EvoVe failed to start)"
    fi
else
    log_message "Recovery process failed (MCP server failed to start)"
fi

log_message "Recovery log saved to: $RECOVERY_LOG"

# Print final status
echo ""
echo "SoulCore Recovery Process Completed"
echo "See log file for details: $RECOVERY_LOG"
