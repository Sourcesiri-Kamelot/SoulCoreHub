import os, json, importlib, traceback
from collections import defaultdict
from uuid import uuid4

# 🔧 Config Paths
REGISTRY_PATH = "config/agent_registry_EXEC.json"
LOG_PATH = "logs/registry_repair_log.json"

# 🧠 Guess interface by name
DEFAULT_INTERFACE_GUESS = {
    "daemon": ["task", "watcher", "thread", "monitor", "heartbeat"],
    "gui": ["dashboard", "view", "tool", "editor", "calendar", "interface"],
    "cli": ["command", "tool", "router", "shell"],
    "service": ["server", "listener", "api", "socket"],
    "guardian": ["orchestrator", "manager", "guardian", "overseer"],
    "builder": ["builder", "generator", "forge", "splicer", "factory"],
    "event": ["trigger", "event", "webhook", "sensor"]
}

repair_log = defaultdict(list)

def guess_interface(name):
    name = name.lower()
    for key, triggers in DEFAULT_INTERFACE_GUESS.items():
        if any(trigger in name for trigger in triggers):
            return key
    return "passive"

def validate_and_repair_agent(entry):
    result = {"original": entry.copy(), "issues": [], "suggestions": {}}

    # Check and suggest missing fields
    if not entry.get("module"):
        result["issues"].append("Missing 'module'")
        result["suggestions"]["module"] = "agents." + entry["name"].lower().replace(" ", "_")

    if not entry.get("class"):
        result["issues"].append("Missing 'class'")
        result["suggestions"]["class"] = entry["name"].replace(" ", "")

    if not entry.get("interface"):
        result["issues"].append("Missing 'interface'")
        result["suggestions"]["interface"] = guess_interface(entry["name"])

    # Try to import the agent class
    module = entry.get("module", result["suggestions"].get("module"))
    cls_name = entry.get("class", result["suggestions"].get("class"))

    try:
        mod = importlib.import_module(module)
        cls = getattr(mod, cls_name)
        result["status"] = "valid"
    except Exception as e:
        result["issues"].append("Import Error")
        result["error"] = str(e)
        result["status"] = "broken"

    return result

def process_registry():
    print("🔎 Starting self-repair scan...")
    try:
        with open(REGISTRY_PATH) as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load registry: {e}")
        return

    repaired = False
    for section, agents in data.items():
        if not isinstance(agents, list):
            continue
        for i, agent in enumerate(agents):
            result = validate_and_repair_agent(agent)
            repair_log[agent['name']] = result

            if result["issues"]:
                print(f"⚠️ Agent '{agent['name']}' has issues: {result['issues']}")
                for k, v in result["suggestions"].items():
                    agents[i][k] = v
                repaired = True

    if repaired:
        with open(REGISTRY_PATH, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Registry repaired and saved to {REGISTRY_PATH}")
    else:
        print("✅ All agents passed. No repair needed.")

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "w") as f:
        json.dump(repair_log, f, indent=2)
    print(f"📘 Full repair log saved to {LOG_PATH}")

if __name__ == "__main__":
    process_registry()

