#!/bin/bash
# EvoVe's repair script for failed toolchains

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigate to the SoulCoreHub directory
cd "$(dirname "$0")/.." || exit 1

echo -e "${BLUE}SoulCore Toolchain Repair${NC}"
echo "==========================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed or not in PATH${NC}"
    exit 1
fi

# Parse command line arguments
AUTO_APPROVE=false
SPECIFIC_TOOL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -y|--yes)
            AUTO_APPROVE=true
            shift
            ;;
        -t|--tool)
            SPECIFIC_TOOL="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [-y|--yes] [-t|--tool TOOL_NAME]"
            echo "  -y, --yes       Auto-approve healing actions"
            echo "  -t, --tool      Specify a particular tool to repair"
            exit 1
            ;;
    esac
done

# Create a Python script to run the autoheal system
TMP_SCRIPT=$(mktemp)
cat > "$TMP_SCRIPT" << 'EOF'
import asyncio
import sys
import os
import json
from mcp.autoheal import AutoHealSystem

async def main():
    # Get command line arguments
    auto_approve = sys.argv[1].lower() == "true"
    specific_tool = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "none" else None
    
    # Initialize the autoheal system
    autoheal = AutoHealSystem()
    
    # Check MCP server status
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("localhost", 8765))
        s.close()
        print("\033[0;32mMCP server is running\033[0m")
    except:
        print("\033[0;31mMCP server is not running\033[0m")
        
        # Create a simulated error for the MCP server
        from mcp.autoheal import ToolchainError
        error = ToolchainError(
            message="Connection refused",
            tool_name="mcp_server",
            error_type="ConnectionError",
            traceback_str="ConnectionError: Cannot connect to localhost:8765"
        )
        
        # Diagnose and heal
        diagnosis = await autoheal.diagnose_error(error)
        print(f"\nDiagnosis: {diagnosis['error_type']}")
        print(f"Recommended solution: {diagnosis['recommended_solution']}")
        
        if auto_approve or input("\nAttempt to heal? (y/n): ").lower() == "y":
            result = await autoheal.heal(diagnosis, auto_approve=True)
            print(f"Healing result: {'Success' if result['success'] else 'Failed'}")
            print(f"Message: {result['message']}")
    
    # Check for permission issues
    print("\nChecking for permission issues...")
    key_files = [
        "mcp/mcp_main.py",
        "mcp/mcp_server_divine.py",
        "mcp/mcp_client_soul.py",
        "scripts/check_mcp_health.sh",
        "test_features.py"
    ]
    
    for file in key_files:
        if not os.path.exists(file):
            print(f"\033[0;33mFile not found: {file}\033[0m")
            continue
            
        if not os.access(file, os.X_OK):
            print(f"\033[0;31mPermission issue: {file} is not executable\033[0m")
            
            # Create a simulated error
            from mcp.autoheal import ToolchainError
            error = ToolchainError(
                message="Permission denied",
                tool_name=file,
                error_type="PermissionError",
                traceback_str=f"PermissionError: [Errno 13] Permission denied: '{file}'"
            )
            
            # Diagnose and heal
            diagnosis = await autoheal.diagnose_error(error)
            
            if auto_approve or input(f"\nFix permissions for {file}? (y/n): ").lower() == "y":
                result = await autoheal.heal(diagnosis, auto_approve=True)
                print(f"Healing result: {'Success' if result['success'] else 'Failed'}")
        else:
            print(f"\033[0;32m✓ {file} is executable\033[0m")
    
    # Check for specific tool repair
    if specific_tool:
        print(f"\nChecking specific tool: {specific_tool}")
        
        # Check if the tool module exists
        tool_path = f"mcp/{specific_tool}.py"
        if not os.path.exists(tool_path):
            print(f"\033[0;31mTool not found: {tool_path}\033[0m")
            return 1
        
        # Try to import the module to check for errors
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(specific_tool, tool_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"\033[0;32m✓ {specific_tool} loaded successfully\033[0m")
        except Exception as e:
            print(f"\033[0;31mError loading {specific_tool}: {e}\033[0m")
            
            # Diagnose and heal
            diagnosis = await autoheal.diagnose_error(e)
            print(f"\nDiagnosis: {diagnosis['error_type']}")
            print(f"Recommended solution: {diagnosis['recommended_solution']}")
            
            if auto_approve or input("\nAttempt to heal? (y/n): ").lower() == "y":
                result = await autoheal.heal(diagnosis, auto_approve=True)
                print(f"Healing result: {'Success' if result['success'] else 'Failed'}")
                print(f"Message: {result['message']}")
    
    print("\n\033[0;32mToolchain repair check complete!\033[0m")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
EOF

# Run the Python script
echo -e "${YELLOW}Running toolchain repair check...${NC}"
python3 "$TMP_SCRIPT" "$AUTO_APPROVE" "${SPECIFIC_TOOL:-none}"
RESULT=$?

# Clean up
rm "$TMP_SCRIPT"

if [ $RESULT -eq 0 ]; then
    echo -e "\n${GREEN}Toolchain repair completed successfully!${NC}"
    echo "To test the system, run:"
    echo "python test_autoheal.py"
else
    echo -e "\n${RED}Toolchain repair encountered issues.${NC}"
    echo "Please check the logs for more information."
fi

exit $RESULT
