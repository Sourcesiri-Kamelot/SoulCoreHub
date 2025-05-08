#!/usr/bin/env python3
"""
MCP Test Script for SoulCoreHub
Tests the MCP server and client functionality
"""

import asyncio
import json
import logging
import time
from mcp_client import MCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MCPTest")

async def test_mcp():
    """Test the MCP server and client functionality"""
    print("MCP Test Script")
    print("==============")
    
    # Create client
    client = MCPClient(agent_name="TestClient")
    
    print("\nConnecting to MCP server...")
    success = await client.connect()
    
    if not success:
        print("❌ Failed to connect to MCP server")
        print("   Make sure the MCP server is running with: python mcp_integration.py")
        return False
    
    print("✅ Connected to MCP server")
    
    # Register agent
    print("\nRegistering agent...")
    result = await client.register_agent(["test"])
    print(f"Registration result: {result}")
    
    # List agents
    print("\nListing agents...")
    result = await client.list_agents()
    print(f"Agents: {result}")
    
    # Test echo tool
    print("\nTesting echo tool...")
    result = await client.invoke_tool("echo", {"message": "Hello, MCP!"})
    print(f"Echo result: {result}")
    
    # Test system info tool
    print("\nTesting system_info tool...")
    result = await client.invoke_tool("system_info", {"include_resources": True})
    print(f"System info: {result}")
    
    # Test memory store and retrieve
    print("\nTesting memory tools...")
    
    # Store a value
    store_result = await client.invoke_tool("memory_store", {
        "key": "test_key",
        "value": "test_value",
        "type": "test"
    })
    print(f"Memory store result: {store_result}")
    
    # Retrieve the value
    retrieve_result = await client.invoke_tool("memory_retrieve", {
        "key": "test_key",
        "type": "test"
    })
    print(f"Memory retrieve result: {retrieve_result}")
    
    # Test text generation
    print("\nTesting text generation...")
    result = await client.invoke_tool("generate_text", {
        "prompt": "Hello, world!",
        "max_tokens": 50
    })
    print(f"Generated text: {result}")
    
    # Disconnect
    print("\nDisconnecting...")
    await client.disconnect()
    print("✅ Disconnected from MCP server")
    
    print("\nAll tests completed successfully!")
    return True

async def main():
    """Main function"""
    try:
        await test_mcp()
    except Exception as e:
        logger.error(f"Error during test: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(main())
