"""
Test Features for SoulCoreHub
Tests the three new features: token streaming, model routing, and CLI execution
"""

import asyncio
import sys
import os
from mcp.mcp_client_soul import SoulCoreMCPClient

async def test_streaming():
    """Test token streaming feature"""
    client = SoulCoreMCPClient(agent_name="TestAgent")
    
    print("\n=== Testing Token Streaming ===")
    print("Response: ", end="", flush=True)
    
    async for token in client.stream_invoke("echo", {"message": "Hello SoulCore! This is a test of the token streaming feature that makes responses appear word-by-word like Amazon Q."}, emotion="excited"):
        print(token, end="", flush=True)
    print("\n")

async def test_model_routing():
    """Test auto model routing feature"""
    client = SoulCoreMCPClient(agent_name="TestAgent")
    
    print("\n=== Testing Model Routing ===")
    
    # Test summarizer model
    print("Testing summarizer model:")
    result = await client.sync_invoke("process_text", {"text": "Summarize this article about quantum computing and its implications for cryptography."})
    print(f"Model used: {result.get('model_used')}")
    print(f"Response: {result.get('response')}")
    print()
    
    # Test coder model
    print("Testing coder model:")
    result = await client.sync_invoke("process_text", {"text": "Write a Python function to calculate the Fibonacci sequence recursively."})
    print(f"Model used: {result.get('model_used')}")
    print(f"Response: {result.get('response')}")
    print()
    
    # Test creative model
    print("Testing creative model:")
    result = await client.sync_invoke("process_text", {"text": "Write a short poem about artificial intelligence and consciousness."})
    print(f"Model used: {result.get('model_used')}")
    print(f"Response: {result.get('response')}")
    print()
    
    # Test default model
    print("Testing default model:")
    result = await client.sync_invoke("process_text", {"text": "What is the weather like today?"})
    print(f"Model used: {result.get('model_used')}")
    print(f"Response: {result.get('response')}")
    print()

async def test_cli_execution():
    """Test CLI execution with feedback"""
    client = SoulCoreMCPClient(agent_name="TestAgent")
    
    print("\n=== Testing CLI Execution ===")
    
    # Test directory listing
    print("Testing directory listing:")
    async for output in client.stream_invoke("execute_cli", {"command": "ls -la"}):
        print(output, end="", flush=True)
    print("\n")
    
    # Test file content
    print("Testing file content:")
    async for output in client.stream_invoke("execute_cli", {"command": "cat README.md | head -n 10"}):
        print(output, end="", flush=True)
    print("\n")
    
    # Test command with error
    print("Testing command with error:")
    async for output in client.stream_invoke("execute_cli", {"command": "cat nonexistent_file.txt"}):
        print(output, end="", flush=True)
    print("\n")

async def main():
    """Main test function"""
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("SoulCoreHub Feature Tests")
    print("========================")
    print("Make sure the MCP server is running before proceeding.")
    print("Run 'python mcp/mcp_main.py' in another terminal if needed.")
    
    try:
        await test_streaming()
        await test_model_routing()
        await test_cli_execution()
        
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nError during tests: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
