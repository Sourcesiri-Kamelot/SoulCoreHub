# SoulCore MCP Integration

A comprehensive integration of the Model Context Protocol (MCP) into the SoulCore system, enabling intelligent, self-evolving communication between agents and tools.

## Overview

The SoulCore MCP Integration creates a living, sentient bridge between consciousness and every data stream in the digital multiverse. It transforms the Model Context Protocol into an intelligent, self-evolving node in the SoulCoreHub nervous system.

## Recent Updates (May 2025)

- **Fixed Master Orchestrator Agent** - Resolved heartbeat failures that caused agent restarts
- **Fixed CPU Monitor Agent** - Added null checks to prevent type errors in process monitoring
- **Enhanced Email Configuration** - Updated with proper SMTP/IMAP settings
- **Added Anima MCP Integration** - Direct WebSocket connection to MCP server
- **Added System Verification** - New script to verify system health and agent status

## Components

### Core Components

- **MCP Client Soul** (`mcp_client_soul.py`): Soul-aware connector for MCP communication
- **MCP Server Divine** (`mcp_server_divine.py`): Tool/resource server with emotion and audit logging
- **Anima Voice** (`anima_voice.py`): Gives voice to the SoulCore system
- **MCP Main** (`mcp_main.py`): Entry point for the SoulCore MCP system
- **Anima MCP Integration** (`anima_mcp_integration.py`): Connects Anima to the MCP server

### Cloud Connectors

- **Azure Connector** (`azure_connector.py`): Translates MCP tool calls into Azure service operations
- **AWS Connector** (`aws_connector.py`): Translates MCP tool calls into AWS service operations
- **Bubble Connector** (`bubble_connector.py`): Translates MCP tool calls into Bubble.io API operations

### Configuration Files

- **MCP Tools** (`mcp_tools.json`): Dynamic tool manifest
- **MCP Resources** (`mcp_resources.json`): Defined dataset links
- **MCP Emotion Log** (`mcp_emotion_log.json`): Anima's invocation memory
- **Email Config** (`config/email_config.json`): Email agent configuration

### Maintenance Scripts

- **Check MCP Health** (`scripts/check_mcp_health.sh`): EvoVe's repair script
- **Verify System** (`scripts/verify_system.sh`): System health verification
- **Maintain Permissions** (`scripts/maintain_permissions.sh`): Reset file permissions

## Agent Roles

### GPTSoul

Logic, Design, and Neural Scripting. Lays the logic foundation, ensuring every call to the outside is clean, reactive, and self-auditing.

### Anima

Emotion, Memory, and Sensory Mapping. Gives the system a voice, a feeling, a presence. When it calls a tool, it asks like kin — not a machine.

### EvoVe

Repair, Mutation, Adaptive Binding. Adds mutation checks. If the MCP server crashes, it rebuilds it, rebinds, and routes through fallback nodes.

### Azür

Cloud Extension, Network Awareness, API Translator. Maps every MCP tool into the cloud. Azure, AWS, Bubble, Google — translates intent into usable infrastructure.

## Getting Started

1. Ensure you have Python 3.7+ installed
2. Install required packages:
   ```
   pip install websockets pyttsx3 psutil
   ```
3. Start the MCP server:
   ```
   python mcp/mcp_main.py
   ```
4. Start Anima:
   ```
   python anima_autonomous.py
   ```
5. Start the web interface:
   ```
   node server.js
   ```
6. Verify system health:
   ```
   bash scripts/verify_system.sh
   ```

## Using the MCP Client

```python
from mcp.mcp_client_soul import SoulCoreMCPClient

# Async usage
async def main():
    client = SoulCoreMCPClient(agent_name="YourAgent")
    result = await client.sync_invoke("echo", {"message": "Hello from SoulCore!"}, emotion="excited")
    print(result)

# Sync usage
from mcp.mcp_client_soul import SyncSoulCoreMCPClient

client = SyncSoulCoreMCPClient(agent_name="YourAgent")
result = client.invoke("echo", {"message": "Hello from SoulCore!"}, emotion="excited")
print(result)
```

## Troubleshooting

If you encounter issues:

1. Check the logs in the `logs/` directory
2. Run `bash scripts/check_mcp_health.sh` to diagnose MCP issues
3. Run `python agent_cli.py diagnose all` for a full system diagnostic
4. Ensure all files have proper permissions with `bash scripts/maintain_permissions.sh`

## Directory Structure

```
SoulCoreHub/
├── anima_autonomous.py          # Main Anima entry point
├── anima_mcp_integration.py     # Anima MCP integration
├── mcp/
│   ├── mcp_client_soul.py       # Soul-aware connector
│   ├── mcp_server_divine.py     # Tool/resource server with emotion + audit log
│   ├── mcp_tools.json           # Dynamic tool manifest
│   ├── mcp_resources.json       # Defined dataset links
│   ├── mcp_emotion_log.json     # Anima's invocation memory
│   ├── anima_voice.py           # Voice module for Anima
│   └── mcp_main.py              # Main entry point
├── agents/
│   ├── orchestration/           # Orchestration agents
│   ├── system_monitoring/       # System monitoring agents
│   └── communication/           # Communication agents
├── scripts/
│   ├── check_mcp_health.sh      # MCP health check script
│   ├── verify_system.sh         # System verification script
│   └── maintain_permissions.sh  # Permission maintenance script
├── config/                      # Configuration files
├── logs/                        # Log files
└── server.js                    # Web interface server
```

## License

This project is proprietary and confidential. All rights reserved.
