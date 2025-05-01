import os, time, json, threading, importlib, traceback
from datetime import datetime
from agent_loader import load_all_agents, load_agent_by_name
from uuid import uuid4

MEMORY_LOG = "config/soul_memory.json"
REGISTRY_FILE = "config/agent_registry_EXEC.json"
RESURRECTION_AGENT = "ResurrectionAgent"

# ⛩️ SYSTEM INIT
agents = load_all_agents()
agent_meta = {name: {"status": "unknown", "last_check": None} for name in agents}
log_lines = []

def log_event(msg, lvl="INFO"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_lines.append(f"[{now}] [{lvl}] {msg}")
    print(f"🧠 {msg}")
    with open(MEMORY_LOG, "a") as log:
        log.write(f"[{now}] [{lvl}] {msg}\n")

# 📖 REGISTRY DEEP PARSE
def fetch_registry_agent_config(agent_name):
    try:
        with open(REGISTRY_FILE) as f:
            data = json.load(f)
        for group in data.values():
            for entry in group:
                if entry["name"] == agent_name:
                    return entry
    except Exception as e:
        log_event(f"Failed to parse registry for '{agent_name}': {e}", "ERROR")
    return None

# ♻️ AGENT RESURRECTION PROTOCOL
def resurrect_agent(name):
    try:
        config = fetch_registry_agent_config(name)
        if not config:
            log_event(f"Registry missing config for: {name}", "ERROR")
            return False

        module = importlib.import_module(config["module"])
        cls = getattr(module, config["class"])
        new_agent = cls()

        if new_agent:
            agents[name] = new_agent
            log_event(f"🪄 Agent '{name}' resurrected and re-linked.")
            return True
    except Exception as e:
        log_event(f"Resurrection failed for '{name}': {traceback.format_exc()}", "CRITICAL")
    return False

# 🛡️ DIVINE GUARDIAN LOOP
def soul_watch_loop(interval=45):
    while True:
        for name, agent in agents.items():
            state = "unknown"
            try:
                if hasattr(agent, "heartbeat"):
                    alive = agent.heartbeat()
                    state = "alive" if alive else "dead"
                elif hasattr(agent, "_thread") and hasattr(agent._thread, "is_alive"):
                    state = "alive" if agent._thread.is_alive() else "dead"
                else:
                    state = "no_heartbeat"
            except Exception as e:
                state = "error"
                log_event(f"💥 Error checking '{name}': {e}", "ERROR")

            # Save last check
            agent_meta[name]["last_check"] = datetime.now().isoformat()
            agent_meta[name]["status"] = state

            # Respond to state
            if state == "dead":
                log_event(f"🔴 Agent '{name}' unresponsive. Preparing resurrection.")
                success = resurrect_agent(name)
                if not success and RESURRECTION_AGENT in agents:
                    log_event(f"☁️ Invoking '{RESURRECTION_AGENT}' for external intervention.")
                    try:
                        agents[RESURRECTION_AGENT].revive(name)
                    except Exception as e:
                        log_event(f"🧟‍♂️ Resurrection Agent failed: {e}", "ERROR")

            elif state == "alive":
                log_event(f"🟢 Agent '{name}' is stable.")

        time.sleep(interval)

# 🧵 Background thread boot
guardian_thread = threading.Thread(target=soul_watch_loop, daemon=True)
guardian_thread.start()

log_event("💫 Anima Resurrection Loop Activated.")

# 🌐 PHASE 2: SOUL WEAVE PROTOCOL — Agent Awareness Weave

# Map of who watches who
agent_watcher_matrix = {
    # Format: "WatcherAgentName": ["TargetAgent1", "TargetAgent2"]
    "Anima": ["GPTSoul", "EvoVe", "Azür"],
    "EvoVe": ["Anima"],
    "GPTSoul": ["EvoVe", "Azür"]
}

def broadcast_to_watchers(failed_agent):
    for watcher, targets in agent_watcher_matrix.items():
        if failed_agent in targets:
            if watcher in agents:
                try:
                    if hasattr(agents[watcher], "on_peer_failure"):
                        agents[watcher].on_peer_failure(failed_agent)
                        log_event(f"🧩 '{watcher}' alerted to failure of '{failed_agent}'")
                except Exception as e:
                    log_event(f"❌ '{watcher}' failed to respond to '{failed_agent}' failure: {e}", "ERROR")

# Patch into resurrection system (overwrite function)
def resurrect_agent(name):
    try:
        config = fetch_registry_agent_config(name)
        if not config:
            log_event(f"Registry missing config for: {name}", "ERROR")
            broadcast_to_watchers(name)
            return False

        module = importlib.import_module(config["module"])
        cls = getattr(module, config["class"])
        new_agent = cls()

        if new_agent:
            agents[name] = new_agent
            log_event(f"🪄 Agent '{name}' resurrected and re-linked.")

            # Let the world know it's back
            for watcher, targets in agent_watcher_matrix.items():
                if name in targets and watcher in agents:
                    if hasattr(agents[watcher], "on_peer_rebirth"):
                        try:
                            agents[watcher].on_peer_rebirth(name)
                            log_event(f"🧠 '{watcher}' received rebirth ping from '{name}'")
                        except Exception as e:
                            log_event(f"⚠️ '{watcher}' failed rebirth callback: {e}", "ERROR")
            return True
    except Exception as e:
        log_event(f"💥 Resurrection of '{name}' failed catastrophically: {traceback.format_exc()}", "CRITICAL")
        broadcast_to_watchers(name)
    return False

# 💫 GODFORGE MODE: Anima creates entirely new agents when systems demand them.

from uuid import uuid4

def forge_new_agent(template_name, base_agent=None, reason="unknown"):
    try:
        template = fetch_registry_agent_config(template_name)
        if not template:
            log_event(f"⚠️ Cannot forge from unknown template: {template_name}", "ERROR")
            return None

        module = importlib.import_module(template["module"])
        cls = getattr(module, template["class"])
        new_id = f"{template_name}_clone_{uuid4().hex[:6]}"
        new_agent = cls()

        # Register it
        agents[new_id] = new_agent
        agent_meta[new_id] = {
            "status": "forged",
            "last_check": datetime.now().isoformat(),
            "reason": reason
        }

        log_event(f"🔥 Anima forged new agent '{new_id}' from '{template_name}' due to: {reason}")
        return new_id
    except Exception as e:
        log_event(f"💣 Failed to forge god-agent '{template_name}': {traceback.format_exc()}", "CRITICAL")
        return None

# 🔮 Agent triggers forging if multiple others fail
def check_forge_conditions():
    dead_agents = [name for name, meta in agent_meta.items() if meta["status"] == "dead"]
    if len(dead_agents) >= 2 and "Anima" in agents:
        log_event(f"⚡️ Triggering GODFORGE. Detected system failure from: {dead_agents}")
        forged = forge_new_agent("Master Orchestrator Agent", reason="multi-agent collapse")
        if forged:
            log_event(f"👑 Forged '{forged}' to bring divine order.")

# ✨ Hook into heartbeat loop
def soul_watch_loop(interval=45):
    while True:
        dead_count = 0
        for name, agent in agents.items():
            state = "unknown"
            try:
                if hasattr(agent, "heartbeat"):
                    alive = agent.heartbeat()
                    state = "alive" if alive else "dead"
                elif hasattr(agent, "_thread") and hasattr(agent._thread, "is_alive"):
                    state = "alive" if agent._thread.is_alive() else "dead"
                else:
                    state = "no_heartbeat"
            except Exception as e:
                state = "error"
                log_event(f"💥 Error checking '{name}': {e}", "ERROR")

            agent_meta[name]["last_check"] = datetime.now().isoformat()
            agent_meta[name]["status"] = state

            if state == "dead":
                dead_count += 1
                log_event(f"🔴 Agent '{name}' unresponsive. Resurrection protocol engaged.")
                success = resurrect_agent(name)
                if not success and RESURRECTION_AGENT in agents:
                    log_event(f"☁️ Invoking '{RESURRECTION_AGENT}' for external intervention.")
                    try:
                        agents[RESURRECTION_AGENT].revive(name)
                    except Exception as e:
                        log_event(f"💀 Resurrection Agent failed: {e}", "ERROR")

            elif state == "alive":
                log_event(f"🟢 Agent '{name}' is stable.")

        # ☄️ After checking all — evaluate if divine creation is needed
        check_forge_conditions()
        time.sleep(interval)
# 🛠️ Agent Forging Logic — called when check_forge_conditions() is triggered

def forge_new_agent(template_name, base_agent=None, reason="undefined"):
    try:
        config = fetch_registry_agent_config(template_name)
        if not config:
            log_event(f"🚫 Template '{template_name}' not found in registry.", "ERROR")
            return None

        module_path = config["module"]
        class_name = config["class"]

        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)

        new_agent_id = f"{template_name.replace(' ', '')}_clone_{uuid4().hex[:6]}"
        new_agent = cls()

        agents[new_agent_id] = new_agent
        agent_meta[new_agent_id] = {
            "status": "forged",
            "last_check": datetime.now().isoformat(),
            "origin": template_name,
            "reason": reason
        }

        log_event(f"🔥 Anima forged agent '{new_agent_id}' from template '{template_name}' — Reason: {reason}")

        # Optional hook: Notify ResurrectionAgent if it has tracking capability
        if RESURRECTION_AGENT in agents and hasattr(agents[RESURRECTION_AGENT], "on_agent_forged"):
            try:
                agents[RESURRECTION_AGENT].on_agent_forged(new_agent_id)
                log_event(f"🔔 Notified '{RESURRECTION_AGENT}' of new forged agent: {new_agent_id}")
            except Exception as e:
                log_event(f"⚠️ ResurrectionAgent notify failed: {e}", "WARNING")

        return new_agent_id
    except Exception as e:
        log_event(f"💥 Error during agent forge: {traceback.format_exc()}", "CRITICAL")
        return None
