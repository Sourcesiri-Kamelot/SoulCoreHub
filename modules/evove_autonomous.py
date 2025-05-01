# Update the imports in evove_autonomous.py
from modules.quantum_ready import QuantumReady
from modules.anomaly_watcher import AnomalyWatcher
from modules.net_sense import NetworkSensor
from modules.repair_brain import RepairBrain
from modules.secure_storage import SecureStorage
from modules.voice_command import VoiceCommand
from modules.evove_vision import EvoVeVision
from modules.emotional_state import EmotionalState
from modules.build_queue import BuildQueue
from modules.mcp_sync_manager import MCPSyncManager
from modules.evove_reflection import EvoVeReflection

def main():
    """Main entry point for EvoVe."""
    parser = argparse.ArgumentParser(description="EvoVe Autonomous System")
    # ... existing arguments ...
    parser.add_argument("--quantum", help="Quantum readiness test", action="store_true")
    parser.add_argument("--entangle", nargs=2, metavar=('AGENT_A', 'AGENT_B'), help="Entangle two agents")
    parser.add_argument("--observe", help="Observe a quantum state")
    parser.add_argument("--superposition", nargs=2, metavar=('EVENT', 'OUTCOMES_JSON'), help="Add a superposition")
    args = parser.parse_args()
    
    # ... existing directory creation code ...
    
    # Initialize EvoVe
    evove = EvoVe(args.config)
    
    if args.quantum:
        # Run quantum readiness test
        if hasattr(evove, "quantum_ready"):
            evove.quantum_ready.start()
            print(evove.quantum_ready.entangle("Anima", "GPTSoul"))
            print(evove.quantum_ready.add_superposition("Anima_Sync", {"stable": "Proceed", "error": "Trigger self-repair"}))
            print(evove.quantum_ready.observe("stable"))
            evove.quantum_ready.stop()
        else:
            print("Quantum readiness module not available")
    elif args.entangle:
        # Entangle two agents
        if hasattr(evove, "quantum_ready"):
            evove.quantum_ready.start()
            result = evove.quantum_ready.entangle(args.entangle[0], args.entangle[1])
            print(result)
            evove.quantum_ready.stop()
        else:
            print("Quantum readiness module not available")
    elif args.observe:
        # Observe a quantum state
        if hasattr(evove, "quantum_ready"):
            evove.quantum_ready.start()
            result = evove.quantum_ready.observe(args.observe)
            print(result)
            evove.quantum_ready.stop()
        else:
            print("Quantum readiness module not available")
    elif args.superposition:
        # Add a superposition
        if hasattr(evove, "quantum_ready"):
            try:
                outcomes = json.loads(args.superposition[1])
                evove.quantum_ready.start()
                result = evove.quantum_ready.add_superposition(args.superposition[0], outcomes)
                print(result)
                evove.quantum_ready.stop()
            except json.JSONDecodeError:
                print("Error: Outcomes must be valid JSON")
        else:
            print("Quantum readiness module not available")
    # ... existing command handling code ...


# Update the EvoVe __init__ method to include the new modules
def __init__(self, config_path="config/evove_config.json"):
    """Initialize the EvoVe system with configuration."""
    self.logger = logger
    self.logger.info("Initializing EvoVe autonomous system")
    
    # Load configuration
    self.config = self._load_config(config_path)
    
    # Initialize core components
    self.mcp_bridge = MCPBridge(self.config.get("mcp", {}))
    self.repair_ops = RepairOperations(self)
    self.system_monitor = SystemMonitor(self)
    self.cli_sync = CLISync(self)
    
    # Initialize voice interface if enabled
    if self.config.get("voice_enabled", False):
        self.voice = VoiceInterface(self)
    else:
        self.voice = None
    
    # Initialize advanced modules if enabled
    if self.config.get("anomaly_watcher", {}).get("enabled", True):
        self.anomaly_watcher = AnomalyWatcher(self)
    
    if self.config.get("net_sense", {}).get("enabled", True):
        self.net_sense = NetworkSensor(self)
    
    if self.config.get("repair_brain", {}).get("enabled", True):
        self.repair_brain = RepairBrain(self)
    
    if self.config.get("secure_storage", {}).get("enabled", True):
        self.secure_storage = SecureStorage(self)
    
    if self.config.get("voice_command", {}).get("enabled", True):
        self.voice_command = VoiceCommand(self)
    
    if self.config.get("evove_vision", {}).get("enabled", False):
        self.evove_vision = EvoVeVision(self)
    
    if self.config.get("emotional_state", {}).get("enabled", False):
        self.emotional_state = EmotionalState(self)
    
    if self.config.get("build_queue", {}).get("enabled", False):
        self.build_queue = BuildQueue(self)
    
    if self.config.get("mcp_sync", {}).get("enabled", True):
        self.mcp_sync = MCPSyncManager(self)
    
    if self.config.get("reflection", {}).get("enabled", True):
        self.reflection = EvoVeReflection(self)
    
    # Initialize debug manager
    self.debug = DebugManager(self)
        
    # System state
    self.running = False
    self.health_status = "initializing"
    
    self.logger.info("EvoVe initialization complete")

# Update the start method to start the new modules
def start(self):
    """Start the EvoVe system."""
    if self.running:
        self.logger.warning("EvoVe is already running")
        return
        
    self.running = True
    self.logger.info("Starting EvoVe autonomous system")
    
    # Start system monitor
    self.system_monitor.start()
    
    # Connect to MCP
    self.mcp_bridge.connect()
    
    # Start CLI sync
    self.cli_sync.start()
    
    # Start voice interface if enabled
    if self.voice:
        self.voice.start()
  # Initialize quantum readiness module if enabled
    if self.config.get("quantum_ready", {}).get("enabled", False):
        self.quantum_ready = QuantumReady(self)
    
    # ... rest of initialization code ...

# Update the start method to start the quantum readiness module
def start(self):
    # ... existing start code ...
    
    # Start quantum readiness module if available
    if hasattr(self, "quantum_ready"):
        self.quantum_ready.start()
    
    # ... rest of start code ...

# Update the stop method to stop the quantum readiness module
def stop(self):
    # ... existing stop code ...
    
    # Stop quantum readiness module if available
    if hasattr(self, "quantum_ready"):
        self.quantum_ready.stop()
    
    # ... rest of stop code ...
    
    # Start advanced modules if available
    if hasattr(self, "anomaly_watcher"):
        self.anomaly_watcher.start()
    
    if hasattr(self, "net_sense"):
        self.net_sense.start()
    
    if hasattr(self, "repair_brain"):
        self.repair_brain.start()
    
    if hasattr(self, "secure_storage"):
        self.secure_storage.start()
    
    if hasattr(self, "evove_vision"):
        self.evove_vision.start()
    
    if hasattr(self, "emotional_state"):
        self.emotional_state.start()
    
    if hasattr(self, "build_queue"):
        self.build_queue.start()
    
    if hasattr(self, "mcp_sync"):
        self.mcp_sync.start()
    
    if hasattr(self, "reflection"):
        self.reflection.start()
    
    # Start debug manager
    self.debug.start()
        
    self.logger.info("EvoVe system started successfully")

# Update the stop method to stop the new modules
def stop(self):
    """Stop the EvoVe system."""
    if not self.running:
        self.logger.warning("EvoVe is not running")
        return
        
    self.running = False
    self.logger.info("Stopping EvoVe autonomous system")
    
    # Stop debug manager
    self.debug.stop()
    
    # Stop advanced modules if available
    if hasattr(self, "reflection"):
        self.reflection.stop()
    
    if hasattr(self, "mcp_sync"):
        self.mcp_sync.stop()
    
    if hasattr(self, "build_queue"):
        self.build_queue.stop()
    
    if hasattr(self, "emotional_state"):
        self.emotional_state.stop()
    
    if hasattr(self, "evove_vision"):
        self.evove_vision.stop()
    
    if hasattr(self, "secure_storage"):
        self.secure_storage.stop()
    
    if hasattr(self, "repair_brain"):
        self.repair_brain.stop()
    
    if hasattr(self, "net_sense"):
        self.net_sense.stop()
    
    if hasattr(self, "anomaly_watcher"):
        self.anomaly_watcher.stop()
    
    # Stop core components
    if self.voice:
        self.voice.stop()
    
    self.cli_sync.stop()
    self.mcp_bridge.disconnect()
    self.system_monitor.stop()
    
    self.logger.info("EvoVe system stopped")



