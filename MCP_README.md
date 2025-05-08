# Model Context Protocol (MCP) for SoulCoreHub

The Model Context Protocol (MCP) is a standardized communication layer that enables different components of SoulCoreHub to share context, invoke tools, and exchange data.

## Overview

MCP consists of several components:

1. **MCP Server** (`mcp_server.py`): The central WebSocket server that handles communication between components.
2. **MCP Client** (`mcp_client.py`): Client library for connecting to the MCP server.
3. **MCP Tools** (`mcp_tools.py`): Tool implementations that can be invoked through the MCP server.
4. **MCP Integration** (`mcp_integration.py`): Integrates the MCP server with the rest of the system.

## Getting Started

### Starting the MCP Server

```bash
python mcp_integration.py
```

This will start the MCP server on `ws://localhost:8765` by default.

### Testing the MCP Server

```bash
python mcp_test.py
```

This will run a series of tests to verify that the MCP server is working correctly.

## Using the MCP Client

### Synchronous Client

```python
from mcp_client import SyncMCPClient

# Create a client
client = SyncMCPClient(agent_name="MyAgent")

# Connect to the server
client.connect()

# Register the agent
client.register_agent(["capability1", "capability2"])

# Invoke a tool
result = client.invoke_tool("echo", {"message": "Hello, MCP!"})
print(result)

# Disconnect
client.disconnect()
```

### Asynchronous Client

```python
import asyncio
from mcp_client import MCPClient

async def main():
    # Create a client
    client = MCPClient(agent_name="MyAgent")
    
    # Connect to the server
    await client.connect()
    
    # Register the agent
    await client.register_agent(["capability1", "capability2"])
    
    # Invoke a tool
    result = await client.invoke_tool("echo", {"message": "Hello, MCP!"})
    print(result)
    
    # Disconnect
    await client.disconnect()

# Run the async function
asyncio.run(main())
```

## Available Tools

The following tools are available by default:

- `register_agent`: Register an agent with the MCP server
- `list_agents`: List all registered agents
- `echo`: Simple echo tool for testing
- `system_info`: Get system information
- `file_read`: Read a file
- `file_write`: Write to a file
- `execute_command`: Execute a command
- `memory_store`: Store data in memory
- `memory_retrieve`: Retrieve data from memory
- `generate_text`: Generate text using a local model

## Adding Custom Tools

You can add custom tools to the MCP server by registering them with the `mcp_tools` instance:

```python
from mcp_tools import mcp_tools

async def my_custom_tool(parameters, agent="system", emotion="neutral"):
    # Tool implementation
    return {"result": "Custom tool result"}

# Register the tool
mcp_tools.register_tool("my_custom_tool", my_custom_tool)
```

## Architecture

```
+----------------+     +----------------+     +----------------+
|                |     |                |     |                |
|  Component A   |     |  Component B   |     |  Component C   |
|                |     |                |     |                |
+-------+--------+     +-------+--------+     +-------+--------+
        |                      |                      |
        v                      v                      v
+-------+----------------------+----------------------+--------+
|                                                             |
|                        MCP Client                           |
|                                                             |
+------------------------------+------------------------------+
                               |
                               v
+------------------------------+------------------------------+
|                                                             |
|                        MCP Server                           |
|                                                             |
+------------------------------+------------------------------+
                               |
                               v
+------------------------------+------------------------------+
|                                                             |
|                        MCP Tools                            |
|                                                             |
+-------------------------------------------------------------+
```

## Protocol Specification

### Message Format

All messages are JSON objects with the following structure:

```json
{
  "request_id": "unique-request-id",
  "tool": "tool-name",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "stream": false,
  "agent": "agent-name",
  "emotion": "neutral"
}
```

### Response Format

Non-streaming responses:

```json
{
  "request_id": "unique-request-id",
  "result": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

Streaming responses:

```json
{
  "request_id": "unique-request-id",
  "type": "token",
  "content": "token-content"
}
```

End of stream:

```json
{
  "request_id": "unique-request-id",
  "type": "end"
}
```

Error responses:

```json
{
  "request_id": "unique-request-id",
  "error": "Error message"
}
```

## Security Considerations

- The MCP server does not currently implement authentication or encryption
- It is intended for local use only
- Do not expose the MCP server to the internet without proper security measures
