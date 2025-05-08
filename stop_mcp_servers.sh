#!/bin/bash
# Stop all MCP servers for SoulCoreHub

echo "Stopping SoulCoreHub MCP Servers..."
cd ~/SoulCoreHub/logs

# Stop each MCP server using its PID file
for server in code_focus_mcp web_design_mcp logic_core_mcp creativity_mcp hacking_mcp cpu_mcp evolution_mcp; do
  if [ -f "${server}.pid" ]; then
    pid=$(cat "${server}.pid")
    echo "Stopping ${server} (PID: ${pid})..."
    kill $pid 2>/dev/null || echo "Process ${pid} not found"
    rm "${server}.pid"
  else
    echo "PID file for ${server} not found"
  fi
done

# Make sure all servers are stopped
echo "Checking for any remaining MCP processes..."
pkill -f "python3.*mcp.py" 2>/dev/null

echo "All MCP servers stopped."
