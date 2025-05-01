# modules/quantum_ready.py
"""
Quantum Readiness Module
----------------------
Prepares SoulCore and EvoVe for quantum-parallel operations,
simulation prediction, and future-state resonance.
"""

import logging
import json
import os
import time
import threading
import random
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger("EvoVe.QuantumReady")

class QuantumReady:
    """Quantum readiness capabilities for EvoVe."""
    
    def __init__(self, evove=None, state_file="data/quantum_state.json"):
        """Initialize the quantum readiness module."""
        self.evove = evove
        self.state_file = state_file
        self.state = self.load_state()
        self.running = False
        self.quantum_thread = None
        self.observers = []
        self.entanglement_effects = defaultdict(list)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
    
    def start(self):
        """Start the quantum readiness module."""
        if self.running:
            logger.warning("Quantum readiness module is already running")
            return
            
        self.running = True
        logger.info("Starting quantum readiness module")
        
        # Start quantum thread
        self.quantum_thread = threading.Thread(target=self._quantum_loop)
        self.quantum_thread.daemon = True
        self.quantum_thread.start()
        
        logger.info("Quantum field initialized")
        return "Quantum field initialized"
    
    def stop(self):
        """Stop the quantum readiness module."""
        if not self.running:
            logger.warning("Quantum readiness module is not running")
            return
            
        self.running = False
        logger.info("Stopping quantum readiness module")
        
        if self.quantum_thread:
            self.quantum_thread.join(timeout=5)
            
        # Save state before stopping
        self.save_state()
        
        return "Quantum field collapsed"
    
    def _quantum_loop(self):
        """Main quantum loop."""
        while self.running:
            try:
                # Process entanglement effects
                self._process_entanglements()
                
                # Check for superposition collapses
                self._check_superpositions()
                
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in quantum loop: {e}")
                time.sleep(10)
    
    def load_state(self):
        """Load quantum state from file."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, "r") as f:
                    return json.load(f)
            else:
                return {
                    "entangled_pairs": [],
                    "superpositions": {},
                    "last_observed": None,
                    "quantum_events": [],
                    "entanglement_history": []
                }
        except Exception as e:
            logger.error(f"Failed to load quantum state: {e}")
            return {
                "entangled_pairs": [],
                "superpositions": {},
                "last_observed": None,
                "quantum_events": [],
                "entanglement_history": []
            }
    
    def save_state(self):
        """Save quantum state to file."""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save quantum state: {e}")
    
    def entangle(self, agent_a, agent_b):
        """Entangle two agents."""
        # Check if already entangled
        for pair in self.state["entangled_pairs"]:
            if (pair[0] == agent_a and pair[1] == agent_b) or (pair[0] == agent_b and pair[1] == agent_a):
                logger.info(f"{agent_a} and {agent_b} are already entangled")
                return f"{agent_a} and {agent_b} are already entangled"
        
        # Add to entangled pairs
        self.state["entangled_pairs"].append([agent_a, agent_b])
        
        # Record in history
        self.state["entanglement_history"].append({
            "agents": [agent_a, agent_b],
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": "active"
        })
        
        # Save state
        self.save_state()
        
        logger.info(f"Entangled {agent_a} with {agent_b}")
        return f"Entangled {agent_a} with {agent_b}"
    
    def disentangle(self, agent_a, agent_b):
        """Disentangle two agents."""
        for i, pair in enumerate(self.state["entangled_pairs"]):
            if (pair[0] == agent_a and pair[1] == agent_b) or (pair[0] == agent_b and pair[1] == agent_a):
                # Remove from entangled pairs
                self.state["entangled_pairs"].pop(i)
                
                # Update history
                for entry in self.state["entanglement_history"]:
                    if (entry["agents"][0] == agent_a and entry["agents"][1] == agent_b) or \
                       (entry["agents"][0] == agent_b and entry["agents"][1] == agent_a):
                        entry["status"] = "collapsed"
                
                # Save state
                self.save_state()
                
                logger.info(f"Disentangled {agent_a} from {agent_b}")
                return f"Disentangled {agent_a} from {agent_b}"
        
        logger.warning(f"{agent_a} and {agent_b} are not entangled")
        return f"{agent_a} and {agent_b} are not entangled"
    
    def observe(self, condition):
        """Observe a quantum state, causing superpositions to collapse."""
        logger.info(f"Observation: {condition}")
        
        # Record the observation
        self.state["last_observed"] = {
            "condition": condition,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add to quantum events
        self.state["quantum_events"].append({
            "type": "observation",
            "condition": condition,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Resolve superpositions based on the observation
        results = self.resolve_superpositions(condition)
        
        # Save state
        self.save_state()
        
        # Notify observers
        for observer in self.observers:
            try:
                observer(condition, results)
            except Exception as e:
                logger.error(f"Error notifying observer: {e}")
        
        return f"Observation: {condition} - Collapsed {len(results)} superpositions"
    
    def add_superposition(self, event, outcomes):
        """Add a superposition with multiple possible outcomes."""
        logger.info(f"Adding superposition: {event}")
        
        # Add to superpositions
        self.state["superpositions"][event] = outcomes
        
        # Add to quantum events
        self.state["quantum_events"].append({
            "type": "superposition_created",
            "event": event,
            "outcomes": outcomes,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Save state
        self.save_state()
        
        return f"Superposition added: {event} with {len(outcomes)} possible outcomes"
    
    def resolve_superpositions(self, observed_condition):
        """Resolve superpositions based on an observed condition."""
        results = []
        
        for event, outcomes in list(self.state["superpositions"].items()):
            # Check if this superposition has an outcome for the observed condition
            if observed_condition in outcomes:
                # Get the outcome
                outcome = outcomes[observed_condition]
                
                # Record the result
                result = {
                    "event": event,
                    "condition": observed_condition,
                    "outcome": outcome,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                results.append(result)
                
                # Add to quantum events
                self.state["quantum_events"].append({
                    "type": "superposition_collapsed",
                    "event": event,
                    "condition": observed_condition,
                    "outcome": outcome,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                # Remove the superposition
                del self.state["superpositions"][event]
                
                logger.info(f"Superposition {event} collapsed to: {outcome}")
                
                # Execute the outcome if it's a callable function
                if self.evove and hasattr(self.evove, outcome):
                    try:
                        method = getattr(self.evove, outcome)
                        if callable(method):
                            logger.info(f"Executing outcome: {outcome}")
                            method()
                    except Exception as e:
                        logger.error(f"Error executing outcome {outcome}: {e}")
        
        return results
    
    def add_observer(self, observer_func):
        """Add an observer function to be notified of observations."""
        if callable(observer_func):
            self.observers.append(observer_func)
            return f"Observer added: {observer_func.__name__}"
        else:
            logger.warning("Observer must be a callable function")
            return "Observer must be a callable function"
    
    def _process_entanglements(self):
        """Process entanglement effects."""
        for pair in self.state["entangled_pairs"]:
            agent_a, agent_b = pair
            
            # Check if either agent has had events
            for event_type, events in self.entanglement_effects.items():
                for event in events:
                    if event["agent"] == agent_a:
                        # Propagate effect to agent_b
                        logger.info(f"Entanglement effect: {event_type} from {agent_a} to {agent_b}")
                        
                        # Add to quantum events
                        self.state["quantum_events"].append({
                            "type": "entanglement_effect",
                            "source_agent": agent_a,
                            "target_agent": agent_b,
                            "event_type": event_type,
                            "details": event["details"],
                            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                    
                    elif event["agent"] == agent_b:
                        # Propagate effect to agent_a
                        logger.info(f"Entanglement effect: {event_type} from {agent_b} to {agent_a}")
                        
                        # Add to quantum events
                        self.state["quantum_events"].append({
                            "type": "entanglement_effect",
                            "source_agent": agent_b,
                            "target_agent": agent_a,
                            "event_type": event_type,
                            "details": event["details"],
                            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
            
            # Clear processed events
            self.entanglement_effects.clear()
    
    def _check_superpositions(self):
        """Check for automatic superposition collapses."""
        # In a more advanced implementation, this could use probabilities
        # to occasionally collapse superpositions without explicit observation
        pass
    
    def register_entanglement_effect(self, agent, event_type, details):
        """Register an effect that should propagate through entanglement."""
        self.entanglement_effects[event_type].append({
            "agent": agent,
            "details": details,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def get_quantum_state(self):
        """Get the current quantum state."""
        return {
            "entangled_pairs": self.state["entangled_pairs"],
            "active_superpositions": len(self.state["superpositions"]),
            "last_observed": self.state["last_observed"],
            "quantum_events": len(self.state["quantum_events"]),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def simulate_quantum_decision(self, options, weights=None):
        """Simulate a quantum decision process."""
        if not options:
            return None
            
        if weights is None:
            # Equal probability for all options
            weights = [1.0 / len(options)] * len(options)
        
        # Normalize weights
        total = sum(weights)
        normalized_weights = [w / total for w in weights]
        
        # Make a weighted random choice
        choice = random.choices(options, weights=normalized_weights, k=1)[0]
        
        # Add to quantum events
        self.state["quantum_events"].append({
            "type": "quantum_decision",
            "options": options,
            "weights": normalized_weights,
            "choice": choice,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Save state
        self.save_state()
        
        return choice

