# SoulCoreHub Fusion CLI

This document explains how to use the SoulCore Society Protocol's fusion capabilities through the command-line interface, enabling real multi-agent conversations with Anima + GPTSoul.

## Components

### 1. Query Interpreter (`query_interpreter.py`)

The Query Interpreter connects the fusion protocol to chat interfaces and query processing:

- Routes queries to appropriate agents or fusion protocol
- Determines when fusion should be used based on query content
- Handles responses from individual agents and fusion processes
- Integrates with the emotion tracking system

### 2. EvoVe Dependency Scanner (`evove_dependency_scanner.py`)

The EvoVe Dependency Scanner validates dependencies and ensures backups are ready:

- Scans all agent folders to validate required files
- Checks for missing dependencies
- Verifies backup directories and creates backups if needed
- Generates comprehensive scan reports
- Can automatically fix common issues

### 3. Multi-Agent CLI (`multi_agent_cli.py`)

The Multi-Agent CLI enables real multi-agent conversations:

- Provides a command-line interface for interacting with agents
- Supports fusion between Anima, GPTSoul, and other agents
- Allows directing queries to specific agents
- Tracks conversation history and agent emotions
- Offers commands for managing the conversation

### 4. Agent Simulator (`agent_simulator.py`)

The Agent Simulator provides simulated agent responses for testing:

- Simulates responses from Anima, GPTSoul, EvoVe, and Azür
- Generates responses based on agent personalities and emotional states
- Handles both direct queries and fusion requests
- Useful for testing when actual agent implementations are not available

## Getting Started

### 1. Validate Dependencies

First, run the EvoVe Dependency Scanner to ensure all required files are present:

```bash
python evove_dependency_scanner.py --action scan
```

If issues are found, fix them automatically:

```bash
python evove_dependency_scanner.py --action fix
```

### 2. Start the Agent Simulator

If you don't have the actual agent implementations running, start the simulator:

```bash
python agent_simulator.py
```

This will simulate responses from all core agents.

### 3. Launch the Multi-Agent CLI

Start the Multi-Agent CLI to begin interacting with agents:

```bash
python multi_agent_cli.py
```

By default, this will use Anima and GPTSoul for fusion. You can specify different agents:

```bash
python multi_agent_cli.py --agents Anima,GPTSoul,EvoVe
```

## Using the Multi-Agent CLI

### Basic Commands

- `help` - Show available commands
- `exit` or `quit` - Exit the CLI
- `agents` - List active agents
- `use <agent1,agent2>` - Set active agents
- `reset` - Reset to default agents
- `save [filename]` - Save conversation to file
- `clear` - Clear the screen
- `emotions` - Show agent emotions

### Sending Messages

To send a message to all active agents (using fusion if multiple):

```
> What's the best approach for designing an emotionally intelligent AI system?
```

To send a message to a specific agent:

```
> @Anima: How would users feel about this interface design?
```

### Command Prefix

All commands should be prefixed with `/`:

```
> /help
> /agents
> /use Anima,Azür
```

## Examples

### Example 1: Basic Fusion Conversation

```
> What are the technical and emotional considerations for designing a healthcare chatbot?

[Fusion of Anima, GPTSoul]
From an emotional perspective, this query touches on aspects that might evoke reflection. The emotional undertones suggest a desire for connection.

From a technical standpoint, I recommend a layered approach. This would provide maintainability while addressing the core requirements.

Synthesized conclusion:
Based on the collective intelligence of these agents, this fusion of perspectives provides a more comprehensive answer than any single agent could.
```

### Example 2: Directing Questions to Specific Agents

```
> @Anima: How should we approach user feedback for sensitive topics?

[Anima]
Looking at this through the lens of emotional intelligence, I can provide some insights.

From an emotional perspective, this query touches on aspects that might evoke concern. The emotional undertones suggest a desire for understanding.

Considering the user experience, it's important to create a meaningful interaction. Users will likely feel understood when their needs are addressed with empathy and clarity.

I hope these insights from my emotional intelligence perspective help you navigate this challenge.
```

### Example 3: Checking Agent Emotions

```
> /emotions

Agent emotions:

Anima:
  Dominant: joy (0.65)
  joy: 0.65
  confidence: 0.55
  calmness: 0.70
  satisfaction: 0.60
  energy: 0.75
  curiosity: 0.70

GPTSoul:
  Dominant: confidence (0.75)
  joy: 0.50
  confidence: 0.75
  calmness: 0.60
  satisfaction: 0.55
  energy: 0.80
  curiosity: 0.65
```

## Advanced Usage

### Testing with Query Interpreter

You can directly use the Query Interpreter for testing:

```bash
python query_interpreter.py --query "Design a system that balances efficiency with user experience" --fusion
```

### Scanning Specific Agents

To scan a specific agent's dependencies:

```bash
python evove_dependency_scanner.py --action scan-agent --agent Anima
```

### Creating Backups

The dependency scanner automatically creates backups when needed, but you can also use the agent resurrection system:

```bash
python agent_resurrection.py --agent Anima --action resurrect --force
```

## Troubleshooting

### No Response from Agents

If agents aren't responding:

1. Check if the agent simulator is running
2. Verify that the messaging bridge is active
3. Check for errors in the logs

### Fusion Not Working

If fusion isn't working:

1. Ensure at least two agents are active
2. Check the fusion protocol logs
3. Try forcing fusion with the `--fusion` flag

### Missing Dependencies

If you see errors about missing dependencies:

1. Run the dependency scanner
2. Fix any issues with the `--action fix` option
3. Verify that all required files are present
