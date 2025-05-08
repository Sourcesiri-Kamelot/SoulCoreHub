# SoulCore Society Protocol

The SoulCore Society Protocol is an advanced agent orchestration layer for SoulCoreHub that enables agent-to-agent collaboration, memory fusion, delegated tasks, emotional state logging, and resurrection of failed agents.

## Components

### 1. Agent Messaging Bridge (`agent_messaging_bridge.py`)

A live messaging system that enables communication between all agents in the SoulCoreHub ecosystem:

- Allows any MCP agent or core agent (Anima, GPTSoul, EvoVe, Azür) to send tasks or messages to other agents
- Logs all communications with sender, receiver, intent, message, and timestamp
- Stores communication history in `agent_society_log.json`
- Provides callback registration for real-time message handling

**Usage:**
```python
from agent_messaging_bridge import get_bridge

# Get the messaging bridge
bridge = get_bridge()

# Send a message
bridge.send_message(
    sender="Anima",
    receiver="GPTSoul",
    intent="task_delegation",
    message="Please analyze this code snippet",
    priority=2
)

# Get messages for an agent
messages = bridge.get_messages("Anima", limit=5)

# Get conversation history between two agents
history = bridge.get_conversation_history("Anima", "GPTSoul", limit=10)
```

### 2. Fusion Protocol (`fusion_protocol.py`)

Enables multiple agents to collaborate on complex requests:

- Combines the knowledge and capabilities of two or more agents
- Merges memory logs, personalities, and RAG context
- Returns results labeled with all participating agents' signatures
- Can be triggered automatically based on query intent

**Usage:**
```python
from fusion_protocol import get_fusion_protocol

# Get the fusion protocol
protocol = get_fusion_protocol()

# Request a fusion
fusion_id = protocol.request_fusion(
    requester="User",
    agents=["Anima", "GPTSoul"],
    query="Analyze the emotional impact of this code architecture",
    timeout=60
)

# Check fusion status
status = protocol.get_fusion_status(fusion_id)

# Check if a query should trigger fusion
should_fuse, recommended_agents = protocol.should_fuse(
    "Compare and contrast these approaches from both technical and emotional perspectives"
)
```

### 3. Agent Emotion State (`agent_emotion_state.py`)

Tracks and manages the emotional states of agents:

- Maintains a lightweight emotion tracker for each agent
- Logs emotional state based on response length, confidence, or feedback
- Stores emotion logs in `agent_emotion_log.json`
- Subtly influences agent response tone based on emotional state

**Usage:**
```python
from agent_emotion_state import get_emotion_tracker

# Get the emotion tracker
tracker = get_emotion_tracker()

# Get an agent's emotional state
emotions = tracker.get_agent_emotion("Anima")

# Update emotions
tracker.update_emotions(
    "Anima",
    {"joy": 0.1, "confidence": -0.05},
    source="user_feedback"
)

# Analyze a response to update emotions
tracker.analyze_response("Anima", "I'm not entirely sure about this approach...")

# Modify text based on emotional state
modified_text = tracker.modify_text_with_emotion("Anima", "Here's the solution to your problem.")
```

### 4. Agent Resurrection (`agent_resurrection.py`)

Detects and resurrects failed agents:

- Monitors agent health based on response rate, error rate, and satisfaction
- Creates backups of agent files before resurrection attempts
- Restores from backups when issues are detected
- Logs resurrection attempts in `agent_resurrection_log.json`

**Usage:**
```python
from agent_resurrection import get_resurrection_engine

# Get the resurrection engine
engine = get_resurrection_engine()

# Check if an agent needs resurrection
needs_resurrection, reason = engine.needs_resurrection("Anima")

# Resurrect an agent
success = engine.resurrect_agent("Anima")

# Get resurrection history
history = engine.get_resurrection_history("Anima", limit=5)

# Analyze failure patterns
analysis = engine.analyze_failure_patterns("Anima")
```

### 5. SoulCore Society (`soulcore_society.py`)

The main orchestration module that integrates all components:

- Initializes and manages all protocol components
- Runs periodic health checks on all agents
- Handles society-wide messaging
- Provides a command-line interface for protocol management

**Usage:**
```bash
# Start the SoulCore Society Protocol
python soulcore_society.py --action start

# Check status of all agents and components
python soulcore_society.py --action status

# Send a message to all agents
python soulcore_society.py --action message --message "System maintenance scheduled for tonight"

# Stop the protocol
python soulcore_society.py --action stop
```

## Integration with SoulCoreHub

The SoulCore Society Protocol integrates seamlessly with the existing SoulCoreHub infrastructure:

1. **Core Agents**: Works with Anima, GPTSoul, EvoVe, and Azür
2. **MCP Integration**: Connects with MCP servers (8701-8707)
3. **RAG System**: Leverages the existing RAG infrastructure for context-aware responses
4. **Web Interface**: Can be monitored and controlled through the Soul Command Center

## Directory Structure

```
SoulCoreHub/
├── agent_messaging_bridge.py
├── fusion_protocol.py
├── agent_emotion_state.py
├── agent_resurrection.py
├── soulcore_society.py
├── agent_society_log.json
├── agent_emotion_log.json
├── agent_fusion_log.json
├── agent_resurrection_log.json
└── backups/
    ├── anima/
    ├── gptsoul/
    ├── evove/
    └── azur/
```

## Getting Started

1. Ensure all SoulCoreHub components are properly installed
2. Run `chmod +x *.py` to make all scripts executable
3. Start the SoulCore Society Protocol:
   ```bash
   python soulcore_society.py --action start
   ```
4. Monitor agent health and interactions:
   ```bash
   python soulcore_society.py --action status
   ```

## Advanced Usage

### Agent Fusion Example

```python
from fusion_protocol import get_fusion_protocol
from agent_messaging_bridge import get_bridge

# Initialize components
bridge = get_bridge()
protocol = get_fusion_protocol()

# Register a callback for fusion responses
def handle_fusion_response(message):
    if message["intent"] == "fusion_response":
        result = message["message"]
        print(f"Fusion result from {', '.join(result['agents'])}:")
        print(result["response"])

bridge.register_callback("MyApplication", handle_fusion_response)

# Request a fusion
fusion_id = protocol.request_fusion(
    requester="MyApplication",
    agents=["Anima", "GPTSoul"],
    query="Design an emotionally resonant user interface for a healthcare application",
    timeout=120
)

print(f"Requested fusion with ID: {fusion_id}")
```

### Emotion-Aware Responses

```python
from agent_emotion_state import get_emotion_tracker

tracker = get_emotion_tracker()

# Update emotions based on user interaction
tracker.update_emotions(
    "Anima",
    {"joy": 0.2, "confidence": 0.1},
    source="user_feedback",
    context={"feedback_type": "positive"}
)

# Generate a response
response = "Here's the solution to your problem..."

# Modify the response based on emotional state
emotion_aware_response = tracker.modify_text_with_emotion("Anima", response)
```

### Agent Resurrection

```python
from agent_resurrection import get_resurrection_engine

engine = get_resurrection_engine()

# Check all core agents
for agent in ["Anima", "GPTSoul", "EvoVe", "Azür"]:
    health = engine.check_agent_health(agent)
    print(f"{agent} health score: {health['health_score']:.2f}")
    
    if health["health_score"] < 0.5:
        print(f"Attempting to resurrect {agent}...")
        success = engine.resurrect_agent(agent)
        print(f"Resurrection {'successful' if success else 'failed'}")
```
