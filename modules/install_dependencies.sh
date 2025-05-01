#!/bin/bash
# EvoVe dependency installer
# This script installs all required dependencies for the EvoVe system

# Configuration
LOG_FILE="logs/install.log"
PYTHON_VERSION="3.8"  # Minimum required version

# Ensure log directory exists
mkdir -p $(dirname "$LOG_FILE")

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check Python version
check_python() {
    log "Checking Python version"
    
    if command -v python3 &>/dev/null; then
        local version=$(python3 --version | cut -d' ' -f2)
        log "Found Python $version"
        
        # Compare versions
        if [[ "$(printf '%s\n' "$PYTHON_VERSION" "$version" | sort -V | head -n1)" = "$PYTHON_VERSION" ]]; then
            log "Python version is sufficient"
            return 0
        else
            log "Python version is too old, need at least $PYTHON_VERSION"
            return 1
        fi
    else
        log "Python 3 not found"
        return 1
    fi
}

# Install Python dependencies
install_python_deps() {
    log "Installing Python dependencies"
    
    # Create requirements.txt if it doesn't exist
    if [ ! -f "requirements.txt" ]; then
        log "Creating requirements.txt"
        cat > requirements.txt << EOF
websocket-client>=1.2.1
websockets>=10.0
psutil>=5.8.0
pyttsx3>=2.90
requests>=2.26.0
EOF
    fi
    
    # Install dependencies
    log "Running pip install"
    python3 -m pip install -r requirements.txt --upgrade
    
    if [ $? -eq 0 ]; then
        log "Python dependencies installed successfully"
        return 0
    else
        log "Failed to install Python dependencies"
        return 1
    fi
}

# Install system dependencies
install_system_deps() {
    log "Checking system dependencies"
    
    local os_type=$(uname -s)
    
    if [ "$os_type" = "Linux" ]; then
        log "Detected Linux system"
        
        # Check for package manager
        if command -v apt-get &>/dev/null; then
            log "Using apt package manager"
            sudo apt-get update
            sudo apt-get install -y netcat python3-dev build-essential
        elif command -v yum &>/dev/null; then
            log "Using yum package manager"
            sudo yum install -y nc python3-devel gcc
        elif command -v pacman &>/dev/null; then
            log "Using pacman package manager"
            sudo pacman -Sy --noconfirm netcat python-pip
        else
            log "Unsupported package manager, please install dependencies manually"
            return 1
        fi
        
    elif [ "$os_type" = "Darwin" ]; then
        log "Detected macOS system"
        
        # Check for Homebrew
        if command -v brew &>/dev/null; then
            log "Using Homebrew package manager"
            brew install netcat
        else
            log "Homebrew not found, please install it or install dependencies manually"
            return 1
        fi
        
    else
        log "Unsupported operating system: $os_type"
        return 1
    fi
    
    log "System dependencies installed successfully"
    return 0
}

# Create directory structure
create_directories() {
    log "Creating directory structure"
    
    mkdir -p mcp
    mkdir -p config
    mkdir -p logs
    mkdir -p backups
    mkdir -p modules
    mkdir -p scripts
    mkdir -p data
    
    log "Directory structure created"
}

# Main execution
log "Starting EvoVe dependency installation"

create_directories

if ! check_python; then
    log "Please install Python $PYTHON_VERSION or higher and try again"
    exit 1
fi

if ! install_system_deps; then
    log "Warning: Some system dependencies may not be installed"
fi

if install_python_deps; then
    log "All dependencies installed successfully"
    
    # Make scripts executable
    chmod +x scripts/*.sh
    
    log "Installation complete"
    exit 0
else
    log "Installation failed"
    exit 1
fi

