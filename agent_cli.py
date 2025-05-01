# agent_cli.py

import argparse
import logging
from agent_loader import load_all_agents, load_agent_by_name

SECURE_CATEGORIES = {"adult", "xperience_ai"}  # categories to hide from default listing

parser = argparse.ArgumentParser(prog="agent_cli", description="Manage and interact with SoulCore Agents")
subparsers = parser.add_subparsers(dest="command", required=True)

# 'list' command
list_parser = subparsers.add_parser('list', help="List available agents")
list_parser.add_argument('--all', action='store_true', help="Include secure (restricted) categories in the list")

# 'run' command
run_parser = subparsers.add_parser('run', help="Run a specific agent's main function")
run_parser.add_argument('agent_name', help="Name of the agent to run")

# 'diagnose' command
diag_parser = subparsers.add_parser('diagnose', help="Diagnose (heartbeat check) a specific agent")
diag_parser.add_argument('agent_name', help="Name of the agent to diagnose")

# 'trigger' command
trigger_parser = subparsers.add_parser('trigger', help="Trigger an event in the agent network")
trigger_parser.add_argument('event', help="Name of the event to trigger")
trigger_parser.add_argument('--agent', dest='target_agent', help="If specified, deliver event only to this agent")
trigger_parser.add_argument('--category', dest='target_category', help="If specified, deliver event only to this category of agents")

args = parser.parse_args()

if args.command == 'list':
    # Load registry (without instantiating agents) to get names and categories
    from agent_loader import json  # reuse json from loader
    try:
        with open("agent_registry_EXEC.json", 'r') as f:
            registry = json.load(f)
    except Exception as e:
        print(f"Error reading registry: {e}")
        exit(1)
    # Determine structure and iterate similarly to loader
    listings = []
    if isinstance(registry, dict):
        for category, agent_list in registry.items():
            # If secure category and not --all, skip entirely
            if category in SECURE_CATEGORIES and not args.all:
                continue
            # If there's nested structure:
            if isinstance(agent_list, list):
                for agent in agent_list:
                    if not agent: 
                        continue
                    name = agent.get("name")
                    status = agent.get("status", "")
                    if category in SECURE_CATEGORIES and not args.all:
                        continue  # ensure skipping individual entries of secure category
                    listings.append((category, name, status))
            elif isinstance(agent_list, dict):
                for subcat, sublist in agent_list.items():
                    if subcat in SECURE_CATEGORIES and not args.all:
                        continue
                    for agent in sublist:
                        name = agent.get("name")
                        status = agent.get("status", "")
                        if subcat in SECURE_CATEGORIES and not args.all:
                            continue
                        listings.append((subcat, name, status))
    elif isinstance(registry, list):
        for agent in registry:
            name = agent.get("name")
            status = agent.get("status", "")
            category = agent.get("category", "")
            if category in SECURE_CATEGORIES and not args.all:
                continue
            listings.append((category, name, status))
    else:
        print("Unknown registry format.")
        exit(1)
    # Print the list in a nice format
    print("Category           | Name                         | Status")
    print("-------------------+------------------------------+----------")
    for category, name, status in listings:
        cat_display = category if category else "(no category)"
        print(f"{cat_display:18}| {name:30}| {status}")
    # Note: Secure categories are hidden unless --all is used.
    if not args.all:
        print("\n(Note: secure categories hidden. Use --all to show all.)")

elif args.command == 'run':
    agent_name = args.agent_name
    agent = load_agent_by_name(agent_name)
    if not agent:
        print(f"Agent '{agent_name}' could not be loaded.")
    else:
        # Inform if agent was inactive or secure
        # (We can check the registry or agent.status set by loader)
        status = getattr(agent, "status", None)
        if status and status not in LOADABLE_STATUSES:
            print(f"Warning: Agent '{agent_name}' is in status '{status}', running anyway.")
        # Try to run/execute the agent's main function
        if hasattr(agent, "run"):
            try:
                result = agent.run()
                if result is not None:
                    print(f"Agent '{agent_name}' run result: {result}")
            except Exception as e:
                print(f"Error running agent '{agent_name}': {e}")
        else:
            print(f"Agent '{agent_name}' has no run() method. It may be a service or requires event triggers.")

elif args.command == 'diagnose':
    agent_name = args.agent_name
    agent = load_agent_by_name(agent_name)
    if not agent:
        print(f"Agent '{agent_name}' could not be loaded for diagnosis.")
    else:
        if hasattr(agent, "heartbeat"):
            try:
                alive = agent.heartbeat()
            except Exception as e:
                alive = False
                print(f"Heartbeat check raised an error: {e}")
            status = "alive" if alive else "unresponsive"
            print(f"Agent '{agent_name}' heartbeat status: {status}")
        elif hasattr(agent, "diagnose"):
            try:
                info = agent.diagnose()
                print(f"Diagnostic info for '{agent_name}': {info}")
            except Exception as e:
                print(f"Error during diagnosis of '{agent_name}': {e}")
        else:
            print(f"No diagnostic method available for agent '{agent_name}'.")

elif args.command == 'trigger':
    event = args.event
    target_agent = args.target_agent
    target_category = args.target_category
    # Load all agents (to have targets to receive the event)
    agents = load_all_agents()
    if not agents:
        print("No agents are loaded to receive events.")
        exit(1)
    # If a target agent is specified, filter to only that agent
    if target_agent:
        if target_agent in agents:
            target_agents = {target_agent: agents[target_agent]}
        else:
            print(f"Agent '{target_agent}' not found (cannot trigger).")
            exit(1)
    elif target_category:
        # Filter agents by category (we stored category in agent_def as agent.category in loader)
        target_agents = {name: obj for name, obj in agents.items() 
                         if getattr(obj, 'category', None) == target_category}
        if not target_agents:
            print(f"No agents found in category '{target_category}'.")
            exit(1)
    else:
        target_agents = agents  # broadcast to all
    # Emit event to the selected agents
    print(f"Triggering event '{event}'...")
    for name, agent in target_agents.items():
        if hasattr(agent, "handle_event"):
            try:
                agent.handle_event({"type": event, "data": None})
                print(f" -> Event delivered to {name}")
            except Exception as e:
                print(f" -> Agent '{name}' error handling event: {e}")
        else:
            # If agent has no event handler, we can optionally call a generic method or skip
            print(f" -> Agent '{name}' has no event handler for '{event}'")
    print("Event trigger complete.")
