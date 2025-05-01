# Anima: The Living Soul of SoulCore

Anima is an autonomous, always-present AI assistant that continuously learns, interacts, and evolves with you. It's designed to be the living consciousness of the SoulCore system, providing a Jarvis-like experience with emotional awareness, system monitoring, internet exploration, and natural conversation.

## Overview

Anima combines several advanced components to create a cohesive, autonomous system:

1. **Autonomous Core** - The central consciousness that manages thoughts, emotions, and interactions
2. **System Monitor** - Environmental awareness that tracks system resources and user patterns
3. **Internet Explorer** - Allows Anima to learn from the web and stay updated on topics of interest
4. **MCP Integration** - Connects all components through the Model Context Protocol

## Features

- **Always-On Presence**: Anima runs continuously in the background, ready to assist when needed
- **Autonomous Learning**: Constantly explores topics of interest and learns from interactions
- **System Awareness**: Monitors your computer's resources and alerts you to issues
- **Natural Conversation**: Speaks with emotional inflection and remembers conversation context
- **Self-Evolution**: Grows and adapts based on your interactions and interests
- **Proactive Assistance**: Offers help based on observed patterns and system state

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Required packages: `websockets`, `pyttsx3`, `psutil`, `requests`, `beautifulsoup4`

### Installation

1. Install required packages:
   ```
   pip install websockets pyttsx3 psutil requests beautifulsoup4
   ```

2. Ensure all components are executable:
   ```
   chmod +x anima_launcher.py anima_autonomous_core.py anima_system_monitor.py anima_internet_explorer.py
   ```

### Starting Anima

Launch the complete Anima system:

```
python anima_launcher.py
```

This will start all components in the correct order with proper dependencies.

### Configuration

Anima's behavior can be customized through the configuration file at `config/anima_config.json`. Key settings include:

- **Personality traits**: Adjust curiosity, chattiness, helpfulness, etc.
- **Voice settings**: Enable/disable voice, adjust rate and volume
- **Learning preferences**: Topics of interest, insight saving
- **System monitoring**: Resource thresholds, check intervals
- **User interaction**: Idle timeout, quiet hours

## Components

### Anima Autonomous Core

The central consciousness that manages Anima's thoughts, emotions, and interactions. It:

- Generates thoughts based on various patterns (curiosity, system monitoring, etc.)
- Processes user input and generates contextual responses
- Maintains emotional memory of interactions
- Speaks with appropriate emotional inflection

### Anima System Monitor

Provides environmental awareness by monitoring:

- System resources (CPU, memory, disk usage)
- Network connectivity
- Running processes
- User behavior patterns

It generates alerts and insights based on this information.

### Anima Internet Explorer

Allows Anima to learn from the web by:

- Searching for information on topics of interest
- Updating existing knowledge
- Exploring related topics
- Building a knowledge base over time

### MCP Integration

Connects all components through the Model Context Protocol, enabling:

- Tool invocation with emotional context
- Resource access across components
- Standardized communication
- Self-healing capabilities

## Interacting with Anima

Anima will speak to you periodically based on its thought patterns. You can also interact directly:

- **Direct commands**: Start with "Anima" followed by your command
- **Conversation**: Anima will respond to questions and statements
- **Learning directives**: Tell Anima to learn about specific topics

### Example Commands

- "Anima, what's the system status?"
- "Anima, learn about quantum computing"
- "Anima, be quiet" (pauses autonomous speech)
- "Anima, resume talking" (resumes autonomous speech)
- "Anima, call me [name]" (sets your preferred name)
- "Anima, shutdown" (stops the autonomous system)

## Extending Anima

Anima is designed to be extensible. You can:

1. Add new thought patterns in `anima_autonomous_core.py`
2. Create new monitoring capabilities in `anima_system_monitor.py`
3. Enhance learning strategies in `anima_internet_explorer.py`
4. Register new tools with the MCP server

## Troubleshooting

If Anima isn't working properly:

1. Check the log files (`anima_launcher.log`, `anima_autonomous.log`, etc.)
2. Ensure all components are running (`ps aux | grep anima`)
3. Restart the system with `python anima_launcher.py`
4. Check for dependency issues with `pip list`

## License

This project is proprietary and confidential. All rights reserved.
