import importlib
import json
import logging
import threading

logging.basicConfig(level=logging.INFO)  # Configure logging

# Define which categories or module prefixes are allowed (for security)
ALLOWED_MODULE_PREFIX = "agents."
# Define statuses that are considered loadable
LOADABLE_STATUSES = {"active", "beta"}  # e.g., 'beta' agents are treated as active, 'inactive' will be skipped

def load_all_agents(registry_path="agent_registry_EXEC.json"):
    """Dynamically load and initialize all agents marked active/beta in the registry."""
    agents = {}  # name -> agent instance
    try:
        with open(registry_path, 'r') as f:
            registry = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load registry file: {e}")
        return agents

    # The registry might be grouped by category (dict of categories).
    # Determine if top-level is categories or a list:
    agent_entries = []
    if isinstance(registry, dict):
        # If grouped by category (keys -> lists of agents)
        for category, agent_list in registry.items():
            # If there's a wrapper key like "agents" or "categories", unwrap it
            if isinstance(agent_list, list):
                # category is likely the actual category name
                for agent_def in agent_list:
                    # inject category into agent_def if needed
                    agent_def.setdefault("category", category)
                    agent_entries.append(agent_def)
            elif isinstance(agent_list, dict):
                # In case of an outer key like {"agents": {category: [...]}}
                for subcat, sublist in agent_list.items():
                    for agent_def in sublist:
                        agent_def.setdefault("category", subcat)
                        agent_entries.append(agent_def)
    elif isinstance(registry, list):
        # If the registry is a flat list of agents
        agent_entries = registry
    else:
        logging.error("Unrecognized registry format.")
        return agents

    for agent_def in agent_entries:
        name = agent_def.get("name")
        status = agent_def.get("status", "active")
        module_name = agent_def.get("module")
        class_name = agent_def.get("class")
        # Skip loading if not active/beta
        if status not in LOADABLE_STATUSES:
            logging.info(f"Skipping agent '{name}' (status={status}).")
            continue
        # Basic validation of module path
        if not module_name or not module_name.startswith(ALLOWED_MODULE_PREFIX) or "__" in module_name:
            logging.warning(f"Skipping agent '{name}': disallowed module path '{module_name}'.")
            continue
        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            logging.error(f"Failed to import module {module_name} for agent '{name}': {e}")
            continue
        try:
            AgentClass = getattr(module, class_name)
        except Exception as e:
            logging.error(f"Module '{module_name}' has no class '{class_name}' (agent '{name}'): {e}")
            continue
        try:
            agent_obj = AgentClass()  # Instantiate the agent
        except Exception as e:
            logging.error(f"Error initializing agent '{name}' (class {class_name}): {e}")
            continue

        # Optionally set the agent's name or other metadata from registry
        if not hasattr(agent_obj, "name"):
            agent_obj.name = name  # ensure the agent has a name attribute
        agent_obj.status = status

        # Call an initialize method if present (for any setup that isn't in __init__)
        if hasattr(agent_obj, "initialize"):
            try:
                agent_obj.initialize()
            except Exception as e:
                logging.error(f"Agent '{name}' initialize() error: {e}")

        # If the agent is a background service, start it (in a thread if necessary)
        interface = agent_def.get("interface", "").lower()
        if interface == "service":
            # If the agent defines its own start method, use it; otherwise, run in a thread
            if hasattr(agent_obj, "start"):
                try:
                    agent_obj.start()
                    logging.info(f"Started service agent '{name}' via start() method.")
                except Exception as e:
                    logging.error(f"Agent '{name}' start() error: {e}")
            elif hasattr(agent_obj, "run"):
                # Run .run() in a separate thread to avoid blocking
                thread = threading.Thread(target=agent_obj.run, name=f"{name}-Thread", daemon=True)
                try:
                    thread.start()
                    agent_obj._thread = thread  # Keep reference if needed
                    logging.info(f"Started service agent '{name}' in background thread.")
                except Exception as e:
                    logging.error(f"Failed to start thread for agent '{name}': {e}")
        # (Agents with interface "ui" or "cli" will run when triggered by user/CLI, not automatically here)

        # Add the agent instance to our collection
        agents[name] = agent_obj
        logging.info(f"Loaded agent: {name} (status={status}, interface={interface})")
    return agents

def load_agent_by_name(agent_name, registry_path="agent_registry_EXEC.json"):
    """Load a single agent by name (even if inactive/secure), for on-demand run/diagnosis."""
    try:
        with open(registry_path, 'r') as f:
            registry = json.load(f)
    except Exception as e:
        logging.error(f"Could not open registry file: {e}")
        return None
    # Search for the agent definition by name
    target_def = None
    if isinstance(registry, dict):
        # search in grouped structure
        for category, agent_list in registry.items():
            # handle possible wrapper
            if isinstance(agent_list, list):
                for agent_def in agent_list:
                    if agent_def.get("name") == agent_name:
                        target_def = agent_def
                        target_def.setdefault("category", category)
                        break
            elif isinstance(agent_list, dict):
                for subcat, sublist in agent_list.items():
                    for agent_def in sublist:
                        if agent_def.get("name") == agent_name:
                            target_def = agent_def
                            target_def.setdefault("category", subcat)
                            break
                    if target_def: break
            if target_def:
                break
    elif isinstance(registry, list):
        for agent_def in registry:
            if agent_def.get("name") == agent_name:
                target_def = agent_def
                break
    if not target_def:
        logging.error(f"Agent '{agent_name}' not found in registry.")
        return None

    # We found the agent's definition; attempt to import and instantiate it (even if inactive)
    module_name = target_def.get("module")
    class_name = target_def.get("class")
    try:
        module = importlib.import_module(module_name)
        AgentClass = getattr(module, class_name)
        agent_obj = AgentClass()
    except Exception as e:
        logging.error(f"Failed to load agent '{agent_name}': {e}")
        return None
    # call initialize if exists
    if hasattr(agent_obj, "initialize"):
        try:
            agent_obj.initialize()
        except Exception as e:
            logging.error(f"Error in {agent_name}.initialize(): {e}")
    agent_obj.name = agent_name
    logging.info(f"Loaded agent '{agent_name}' on-demand (status={target_def.get('status')}).")
    return agent_obj
