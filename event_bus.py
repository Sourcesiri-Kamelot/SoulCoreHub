# event_bus.py (or within agent_loader.py)

import logging

class EventBus:
    def __init__(self):
        self.subscribers = []  # list of (agent, [event_types]) subscriptions

    def subscribe(self, agent, event_types=None):
        """
        Subscribe an agent to the bus. 
        event_types: list of event type strings this agent cares about, or None for all.
        """
        self.subscribers.append((agent, event_types or []))
        logging.info(f"Agent '{getattr(agent, 'name', agent)}' subscribed to events: {event_types or 'ALL'}")

    def emit(self, event_type, data=None):
        """
        Emit an event to all subscribed agents. 
        Agents with specified event_types will only get matching events, 
        agents with no filter (all) get everything.
        """
        event = {"type": event_type, "data": data}
        logging.info(f"Emitting event '{event_type}' to agents...")
        for agent, event_types in self.subscribers:
            # check subscription filter
            if event_types and event_type not in event_types:
                continue
            if hasattr(agent, "handle_event"):
                try:
                    agent.handle_event(event)
                    logging.info(f" -> {agent.name} handled event '{event_type}'.")
                except Exception as e:
                    logging.error(f"Agent '{getattr(agent,'name',agent)}' error handling {event_type}: {e}")
            # Optionally, try a fallback method naming convention:
            elif hasattr(agent, f"on_{event_type}"):
                # e.g., agent defines on_SECURITY_ALERT(self, data)
                try:
                    getattr(agent, f"on_{event_type}")(data)
                    logging.info(f" -> {agent.name}.on_{event_type} executed.")
                except Exception as e:
                    logging.error(f"Agent '{agent.name}' error in on_{event_type}: {e}")
        logging.info(f"Event '{event_type}' dispatch complete.")
