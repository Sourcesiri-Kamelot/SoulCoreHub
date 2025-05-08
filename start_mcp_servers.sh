#!/bin/bash
# Start all MCP servers for SoulCoreHub

echo "Starting SoulCoreHub MCP Servers..."
cd ~/SoulCoreHub/mcp_servers

# Start each MCP server in the background
echo "Starting Code Focus MCP (Port 8701)..."
python3 code_focus_mcp.py > ../logs/code_focus_mcp.log 2>&1 &
echo $! > ../logs/code_focus_mcp.pid

echo "Starting Web Design MCP (Port 8702)..."
python3 web_design_mcp.py > ../logs/web_design_mcp.log 2>&1 &
echo $! > ../logs/web_design_mcp.pid

echo "Starting Logic Core MCP (Port 8703)..."
python3 logic_core_mcp.py > ../logs/logic_core_mcp.log 2>&1 &
echo $! > ../logs/logic_core_mcp.pid

echo "Starting Creativity MCP (Port 8704)..."
python3 creativity_mcp.py > ../logs/creativity_mcp.log 2>&1 &
echo $! > ../logs/creativity_mcp.pid

echo "Starting Hacking MCP (Port 8705)..."
python3 hacking_mcp.py > ../logs/hacking_mcp.log 2>&1 &
echo $! > ../logs/hacking_mcp.pid

echo "Starting CPU MCP (Port 8706)..."
python3 cpu_mcp.py > ../logs/cpu_mcp.log 2>&1 &
echo $! > ../logs/cpu_mcp.pid

echo "Starting Evolution MCP (Port 8707)..."
python3 evolution_mcp.py > ../logs/evolution_mcp.log 2>&1 &
echo $! > ../logs/evolution_mcp.pid

echo "All MCP servers started. Check logs in ~/SoulCoreHub/logs/ directory."
echo "Use 'ps aux | grep mcp' to see running servers."
echo "Use 'bash stop_mcp_servers.sh' to stop all servers."
