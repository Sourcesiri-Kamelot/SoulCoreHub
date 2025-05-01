#!/bin/bash
# evove_healthcheck.sh - Script to check the health of the SoulCore system

# Set the base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR" || exit 1

# Create logs directory if it doesn't exist
mkdir -p "$BASE_DIR/logs"

# Function to check if a process is running
check_process() {
    local process_name="$1"
    local process_pattern="$2"
    
    if pgrep -f "$process_pattern" > /dev/null; then
        echo "✅ $process_name is running"
        return 0
    else
        echo "❌ $process_name is not running"
        return 1
    fi
}

# Function to check if a directory exists
check_directory() {
    local dir_name="$1"
    local dir_path="$2"
    
    if [ -d "$dir_path" ]; then
        echo "✅ $dir_name directory exists"
        return 0
    else
        echo "❌ $dir_name directory does not exist"
        return 1
    fi
}

# Function to check file permissions
check_permissions() {
    local file_path="$1"
    local file_name="$(basename "$file_path")"
    
    if [ -f "$file_path" ]; then
        if [ -x "$file_path" ]; then
            echo "✅ $file_name has executable permissions"
            return 0
        else
            echo "❌ $file_name does not have executable permissions"
            return 1
        fi
    else
        echo "❌ $file_name does not exist"
        return 1
    fi
}

# Function to repair permissions
repair_permissions() {
    echo "🔧 Repairing file permissions..."
    
    if [ -f "$BASE_DIR/maintain_permissions.sh" ]; then
        chmod +x "$BASE_DIR/maintain_permissions.sh"
        bash "$BASE_DIR/maintain_permissions.sh"
        echo "✅ Permissions repaired"
    else
        echo "❌ maintain_permissions.sh not found"
        
        # Manual permission repair for key files
        find "$BASE_DIR" -name "*.py" -exec chmod +x {} \;
        find "$BASE_DIR/scripts" -name "*.sh" -exec chmod +x {} \;
        echo "✅ Manually repaired permissions"
    fi
}

# Function to create missing directories
create_missing_directories() {
    echo "🔧 Creating missing directories..."
    
    mkdir -p "$BASE_DIR/mcp"
    mkdir -p "$BASE_DIR/scripts"
    mkdir -p "$BASE_DIR/logs"
    mkdir -p "$BASE_DIR/data"
    mkdir -p "$BASE_DIR/modules"
    mkdir -p "$BASE_DIR/evove"
    mkdir -p "$BASE_DIR/anima"
    mkdir -p "$BASE_DIR/voices"
    mkdir -p "$BASE_DIR/gallery"
    
    echo "✅ Created missing directories"
}

# Function to start MCP server
start_mcp_server() {
    echo "🔧 Starting MCP server..."
    
    if [ -f "$BASE_DIR/mcp/mcp_main.py" ]; then
        cd "$BASE_DIR/mcp" && python mcp_main.py > "$BASE_DIR/logs/mcp_server.log" 2>&1 &
        sleep 2
        
        if pgrep -f "python.*mcp_main.py" > /dev/null; then
            echo "✅ MCP server started successfully"
        else
            echo "❌ Failed to start MCP server"
        fi
    else
        echo "❌ mcp_main.py not found"
    fi
}

# Print header
echo "========================================"
echo "SoulCore System Health Check"
echo "========================================"
echo "Date: $(date)"
echo "System: $(uname -a)"
echo "========================================"

# Check key processes
echo "Checking processes..."
check_process "MCP Server" "python.*mcp_main.py"
mcp_running=$?

check_process "Anima" "python.*anima_"
anima_running=$?

check_process "EvoVe" "python.*evove_autonomous.py"
evove_running=$?

check_process "Web Server" "node.*server.js"
server_running=$?

echo ""

# Check key directories
echo "Checking directories..."
check_directory "MCP" "$BASE_DIR/mcp"
mcp_dir_exists=$?

check_directory "Scripts" "$BASE_DIR/scripts"
scripts_dir_exists=$?

check_directory "Modules" "$BASE_DIR/modules"
modules_dir_exists=$?

check_directory "EvoVe" "$BASE_DIR/evove"
evove_dir_exists=$?

echo ""

# Check key file permissions
echo "Checking file permissions..."
check_permissions "$BASE_DIR/maintain_permissions.sh"
maintain_permissions_executable=$?

if [ -f "$BASE_DIR/mcp/mcp_main.py" ]; then
    check_permissions "$BASE_DIR/mcp/mcp_main.py"
fi

if [ -f "$BASE_DIR/evove_autonomous.py" ]; then
    check_permissions "$BASE_DIR/evove_autonomous.py"
fi

echo ""

# Check system resources
echo "Checking system resources..."
echo "CPU Usage: $(top -l 1 | grep "CPU usage" | awk '{print $3 " " $4 " " $5 " " $6 " " $7 " " $8}')"
echo "Memory Usage: $(vm_stat | grep "Pages active" | awk '{print $3}' | sed 's/\.//')"
echo "Disk Usage: $(df -h / | tail -1 | awk '{print $5}')"

echo ""

# Determine if repairs are needed
repairs_needed=0

if [ $mcp_running -ne 0 ] || [ $mcp_dir_exists -ne 0 ]; then
    repairs_needed=1
fi

if [ $maintain_permissions_executable -ne 0 ]; then
    repairs_needed=1
fi

if [ $modules_dir_exists -ne 0 ] || [ $evove_dir_exists -ne 0 ]; then
    repairs_needed=1
fi

# Perform repairs if needed
if [ $repairs_needed -eq 1 ]; then
    echo "========================================"
    echo "Repairs needed, performing maintenance..."
    echo "========================================"
    
    # Create missing directories
    create_missing_directories
    
    # Repair permissions
    repair_permissions
    
    # Start MCP server if not running
    if [ $mcp_running -ne 0 ]; then
        start_mcp_server
    fi
    
    echo ""
    echo "Maintenance completed."
else
    echo "========================================"
    echo "System health check passed, no repairs needed."
    echo "========================================"
fi

# Exit with status
if [ $repairs_needed -eq 1 ]; then
    exit 1
else
    exit 0
fi
