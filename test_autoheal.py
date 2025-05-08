#!/usr/bin/env python3
"""
Test AutoHeal System for SoulCoreHub
Demonstrates the self-healing capabilities for failed toolchains
"""

import asyncio
import sys
import os
import traceback
from mcp.autoheal import AutoHealSystem, ToolchainError
from mcp.mcp_client_soul import SoulCoreMCPClient

class ToolchainTester:
    """Test class for demonstrating toolchain failures and healing"""
    
    def __init__(self):
        """Initialize the tester"""
        self.autoheal = AutoHealSystem()
        self.client = SoulCoreMCPClient(agent_name="AutoHealTester")
    
    async def test_missing_module(self):
        """Test healing a missing module error"""
        print("\n=== Testing Missing Module Error ===")
        
        try:
            # Simulate a missing module error
            import nonexistent_module
            print("This should not be reached")
        except ImportError as e:
            print(f"Error: {e}")
            
            # Diagnose the error
            diagnosis = await self.autoheal.diagnose_error(e)
            print(f"\nDiagnosis: {diagnosis['error_type']}")
            print(f"Recommended solution: {diagnosis['recommended_solution']}")
            
            # Attempt to heal
            print("\nAttempting to heal...")
            result = await self.autoheal.heal(diagnosis, auto_approve=True)
            print(f"Healing result: {'Success' if result['success'] else 'Failed'}")
            print(f"Message: {result['message']}")
    
    async def test_permission_error(self):
        """Test healing a permission error"""
        print("\n=== Testing Permission Error ===")
        
        # Create a test file without execute permissions
        test_file = "test_permission.sh"
        with open(test_file, 'w') as f:
            f.write("#!/bin/bash\necho 'Hello from test script'")
        
        try:
            # Try to execute it
            os.chmod(test_file, 0o644)  # Read/write but not executable
            os.system(f"./{test_file}")
            
            # This will fail, but we need to simulate the error for diagnosis
            raise ToolchainError(
                message="Permission denied",
                tool_name=test_file,
                error_type="PermissionError",
                traceback_str=f"PermissionError: [Errno 13] Permission denied: '{test_file}'"
            )
        except ToolchainError as e:
            print(f"Error: {e}")
            
            # Diagnose the error
            diagnosis = await self.autoheal.diagnose_error(e)
            print(f"\nDiagnosis: {diagnosis['error_type']}")
            print(f"Recommended solution: {diagnosis['recommended_solution']}")
            
            # Attempt to heal
            print("\nAttempting to heal...")
            result = await self.autoheal.heal(diagnosis, auto_approve=True)
            print(f"Healing result: {'Success' if result['success'] else 'Failed'}")
            print(f"Message: {result['message']}")
            
            # Clean up
            os.remove(test_file)
    
    async def test_connection_error(self):
        """Test healing a connection error"""
        print("\n=== Testing Connection Error ===")
        
        # Check if MCP server is running
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_running = False
        try:
            s.connect(("localhost", 8765))
            server_running = True
            s.close()
        except:
            server_running = False
        
        if server_running:
            print("MCP server is already running, stopping it for the test...")
            os.system("pkill -f 'python.*mcp_main.py'")
            await asyncio.sleep(2)
        
        try:
            # Try to connect to the MCP server (which should be down)
            await self.client.sync_invoke("echo", {"message": "Hello"})
            print("This should not be reached")
        except Exception as e:
            print(f"Error: {e}")
            
            # Create a simulated error with the right format for the autoheal system
            simulated_error = ToolchainError(
                message="Connection refused",
                tool_name="mcp_client",
                error_type="ConnectionError",
                traceback_str="ConnectionError: Cannot connect to localhost:8765"
            )
            
            # Diagnose the error
            diagnosis = await self.autoheal.diagnose_error(simulated_error)
            print(f"\nDiagnosis: {diagnosis['error_type']}")
            print(f"Recommended solution: {diagnosis['recommended_solution']}")
            
            # Attempt to heal
            print("\nAttempting to heal...")
            result = await self.autoheal.heal(diagnosis, auto_approve=True)
            print(f"Healing result: {'Success' if result['success'] else 'Failed'}")
            print(f"Message: {result['message']}")
            
            # Verify the server is now running
            await asyncio.sleep(2)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect(("localhost", 8765))
                print("Server is now running!")
                s.close()
            except:
                print("Server is still not running")
    
    async def test_syntax_error(self):
        """Test healing a syntax error"""
        print("\n=== Testing Syntax Error ===")
        
        # Create a file with a syntax error
        test_file = "test_syntax.py"
        with open(test_file, 'w') as f:
            f.write("def broken_function():\n    print('This is broken'\n")  # Missing closing parenthesis
        
        try:
            # Try to import it
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_module", test_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print("This should not be reached")
        except SyntaxError as e:
            print(f"Error: {e}")
            
            # Diagnose the error
            diagnosis = await self.autoheal.diagnose_error(e)
            print(f"\nDiagnosis: {diagnosis['error_type']}")
            print(f"Recommended solution: {diagnosis['recommended_solution']}")
            
            # Attempt to heal
            print("\nAttempting to heal...")
            result = await self.autoheal.heal(diagnosis, auto_approve=True)
            print(f"Healing result: {'Success' if result['success'] else 'Failed'}")
            print(f"Message: {result['message']}")
            
            if result['success']:
                print("\nVerifying fix...")
                try:
                    spec = importlib.util.spec_from_file_location("test_module", test_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    print("Fix successful! Module now imports correctly.")
                except Exception as e:
                    print(f"Fix failed: {e}")
            
            # Clean up
            os.remove(test_file)
    
    async def test_backup_restore(self):
        """Test backup and restore functionality"""
        print("\n=== Testing Backup and Restore ===")
        
        # Create a backup
        print("Creating backup...")
        backup_path = self.autoheal._create_backup()
        print(f"Backup created at: {backup_path}")
        
        # Modify a file
        test_file = "test_modify.py"
        with open(test_file, 'w') as f:
            f.write("print('Original content')")
        
        print("Modifying file...")
        with open(test_file, 'w') as f:
            f.write("print('Modified content')")
        
        # Restore from backup
        print("Restoring from backup...")
        result = await self.autoheal.restore_backup(backup_path)
        print(f"Restore result: {'Success' if result['success'] else 'Failed'}")
        print(f"Message: {result['message']}")
        
        # Clean up
        os.remove(test_file)

async def main():
    """Main test function"""
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("SoulCoreHub AutoHeal System Tests")
    print("================================")
    print("This script demonstrates the self-healing capabilities of the AutoHeal system.")
    
    tester = ToolchainTester()
    
    try:
        # Run the tests
        await tester.test_permission_error()
        await tester.test_connection_error()
        await tester.test_syntax_error()
        await tester.test_backup_restore()
        
        # Skip the missing module test as it would actually try to install a package
        # await tester.test_missing_module()
        
        print("\nAll tests completed!")
    except Exception as e:
        print(f"\nError during tests: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
