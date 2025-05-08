#!/usr/bin/env python3
"""
Agent CLI for SoulCoreHub
Command-line interface for managing agents
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from agent_loader import load_agent_by_name, load_all_agents, load_registry, init_registry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_cli.log')
    ]
)
logger = logging.getLogger("AgentCLI")

def list_agents(args):
    """List all agents in the registry"""
    registry = load_registry(args.registry)
    if not registry:
        print("❌ Failed to load agent registry")
        return False
    
    print("\n📋 AGENT REGISTRY")
    print("=" * 60)
    
    for category, agents in registry.items():
        print(f"\n📁 {category.upper()}")
        print("-" * 60)
        
        for agent in agents:
            status = "✅" if agent.get("status") == "active" else "❌"
            priority = agent.get("priority", "medium")
            priority_icon = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
            
            print(f"{status} {priority_icon} {agent.get('name')}")
            print(f"   Description: {agent.get('desc')}")
            print(f"   Module: {agent.get('module')}")
            print(f"   Interface: {agent.get('interface')}")
            print()
    
    return True

def activate_agent(args):
    """Activate a specific agent"""
    agent = load_agent_by_name(args.name, args.registry)
    if not agent:
        print(f"❌ Failed to load agent: {args.name}")
        return False
    
    print(f"🚀 Activating agent: {args.name}")
    
    if hasattr(agent, "activate"):
        success = agent.activate()
        if success:
            print(f"✅ Agent {args.name} activated successfully")
        else:
            print(f"❌ Failed to activate agent {args.name}")
        return success
    else:
        print(f"⚠️ Agent {args.name} does not support activation")
        return False

def deactivate_agent(args):
    """Deactivate a specific agent"""
    agent = load_agent_by_name(args.name, args.registry)
    if not agent:
        print(f"❌ Failed to load agent: {args.name}")
        return False
    
    print(f"🛑 Deactivating agent: {args.name}")
    
    if hasattr(agent, "deactivate"):
        success = agent.deactivate()
        if success:
            print(f"✅ Agent {args.name} deactivated successfully")
        else:
            print(f"❌ Failed to deactivate agent {args.name}")
        return success
    else:
        print(f"⚠️ Agent {args.name} does not support deactivation")
        return False

def status_agent(args):
    """Get the status of a specific agent or all agents"""
    if args.name:
        agent = load_agent_by_name(args.name, args.registry)
        if not agent:
            print(f"❌ Failed to load agent: {args.name}")
            return False
        
        print(f"\n📊 STATUS: {args.name}")
        print("=" * 60)
        
        if hasattr(agent, "get_system_state"):
            state = agent.get_system_state()
            print(f"State: {state.get('state', 'unknown')}")
            print(f"Active Agents: {state.get('active_agents', 0)}")
            print(f"Last Activation: {state.get('last_activation', 'unknown')}")
            print(f"Uptime: {state.get('uptime', 0):.2f} seconds")
        else:
            print(f"⚠️ Agent {args.name} does not support status reporting")
        
        return True
    else:
        # Get status of all agents
        agents = load_all_agents(args.registry)
        if not agents:
            print("❌ No agents loaded")
            return False
        
        print("\n📊 SYSTEM STATUS")
        print("=" * 60)
        
        for agent in agents:
            print(f"\n🤖 {agent.name}")
            
            if hasattr(agent, "get_system_state"):
                state = agent.get_system_state()
                print(f"  State: {state.get('state', 'unknown')}")
                print(f"  Active Agents: {state.get('active_agents', 0)}")
                print(f"  Last Activation: {state.get('last_activation', 'unknown')}")
                print(f"  Uptime: {state.get('uptime', 0):.2f} seconds")
            else:
                print(f"  ⚠️ Does not support status reporting")
        
        return True

def diagnose_agent(args):
    """Diagnose a specific agent or component"""
    if args.component == "all":
        print("\n🔍 DIAGNOSING ALL COMPONENTS")
        print("=" * 60)
        
        # Check registry
        registry = load_registry(args.registry)
        if registry:
            print("✅ Agent registry loaded successfully")
        else:
            print("❌ Failed to load agent registry")
        
        # Check agents
        agents = load_all_agents(args.registry)
        print(f"✅ Loaded {len(agents)} agents")
        
        # Check memory directory
        memory_dir = Path("memory")
        if memory_dir.exists() and memory_dir.is_dir():
            print(f"✅ Memory directory exists: {memory_dir}")
        else:
            print(f"❌ Memory directory not found: {memory_dir}")
        
        # Check GPTSoul
        gptsoul = load_agent_by_name("GPTSoul", args.registry)
        if gptsoul:
            print("✅ GPTSoul agent loaded successfully")
            if hasattr(gptsoul, "is_placeholder") and gptsoul.is_placeholder:
                print("⚠️ GPTSoul is a placeholder")
        else:
            print("❌ Failed to load GPTSoul agent")
        
        # Check Anima
        anima = load_agent_by_name("Anima", args.registry)
        if anima:
            print("✅ Anima agent loaded successfully")
            if hasattr(anima, "is_placeholder") and anima.is_placeholder:
                print("⚠️ Anima is a placeholder")
        else:
            print("❌ Failed to load Anima agent")
        
        return True
    
    elif args.component == "registry":
        registry = load_registry(args.registry)
        if not registry:
            print("❌ Failed to load agent registry")
            return False
        
        print("\n🔍 REGISTRY DIAGNOSIS")
        print("=" * 60)
        
        # Count agents by category
        category_counts = {category: len(agents) for category, agents in registry.items()}
        print("Categories:")
        for category, count in category_counts.items():
            print(f"  {category}: {count} agents")
        
        # Count active agents
        active_count = sum(1 for category, agents in registry.items() 
                          for agent in agents if agent.get("status") == "active")
        print(f"Active agents: {active_count}")
        
        # Check for common issues
        issues = []
        
        for category, agents in registry.items():
            for agent in agents:
                if "name" not in agent:
                    issues.append(f"Agent in {category} missing name")
                if "module" not in agent:
                    issues.append(f"Agent {agent.get('name', 'unknown')} missing module")
                if "class" not in agent:
                    issues.append(f"Agent {agent.get('name', 'unknown')} missing class")
        
        if issues:
            print("\nIssues found:")
            for issue in issues:
                print(f"  ⚠️ {issue}")
        else:
            print("\n✅ No issues found in registry")
        
        return True
    
    elif args.component == "mcp":
        print("\n🔍 MCP DIAGNOSIS")
        print("=" * 60)
        
        # Check MCP client
        try:
            from anima_mcp_integration import anima_mcp
            print("✅ MCP client module loaded")
            
            # Check if connect method exists
            if hasattr(anima_mcp, "connect"):
                print("✅ MCP client has connect method")
            else:
                print("❌ MCP client missing connect method")
            
            # Check if client attribute exists
            if hasattr(anima_mcp, "client"):
                print("✅ MCP client has client attribute")
            else:
                print("❌ MCP client missing client attribute")
            
        except ImportError:
            print("❌ Failed to import MCP client module")
        
        # Check MCP server
        mcp_server_path = Path("mcp_server.py")
        if mcp_server_path.exists():
            print(f"✅ MCP server file exists: {mcp_server_path}")
        else:
            print(f"❌ MCP server file not found: {mcp_server_path}")
        
        return True
    
    else:
        print(f"❌ Unknown component: {args.component}")
        return False

def init_agent_registry(args):
    """Initialize a new agent registry"""
    success = init_registry(args.output)
    if success:
        print(f"✅ Agent registry initialized successfully")
        if args.output:
            print(f"   Path: {args.output}")
    else:
        print(f"❌ Failed to initialize agent registry")
    
    return success

def check_registry(args):
    """Check if the agent registry exists"""
    registry_path = args.registry if args.registry else "agent_registry_core.json"
    if os.path.exists(registry_path):
        print(f"✅ Agent registry exists: {registry_path}")
        return True
    else:
        print(f"❌ Agent registry not found: {registry_path}")
        return False

def main():
    """Main function for the Agent CLI"""
    parser = argparse.ArgumentParser(description="SoulCoreHub Agent CLI")
    parser.add_argument("--registry", help="Path to agent registry file")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all agents")
    
    # Activate command
    activate_parser = subparsers.add_parser("activate", help="Activate an agent")
    activate_parser.add_argument("name", help="Name of the agent to activate")
    
    # Deactivate command
    deactivate_parser = subparsers.add_parser("deactivate", help="Deactivate an agent")
    deactivate_parser.add_argument("name", help="Name of the agent to deactivate")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Get agent status")
    status_parser.add_argument("name", nargs="?", help="Name of the agent (optional)")
    
    # Diagnose command
    diagnose_parser = subparsers.add_parser("diagnose", help="Diagnose agent system")
    diagnose_parser.add_argument("component", choices=["all", "registry", "mcp"], 
                               help="Component to diagnose")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize agent registry")
    init_parser.add_argument("output", nargs="?", help="Output path for registry")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check if registry exists")
    check_parser.add_argument("type", choices=["registry"], help="Type to check")
    
    args = parser.parse_args()
    
    if args.command == "list":
        return list_agents(args)
    elif args.command == "activate":
        return activate_agent(args)
    elif args.command == "deactivate":
        return deactivate_agent(args)
    elif args.command == "status":
        return status_agent(args)
    elif args.command == "diagnose":
        return diagnose_agent(args)
    elif args.command == "init":
        return init_agent_registry(args)
    elif args.command == "check":
        return check_registry(args)
    else:
        parser.print_help()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
