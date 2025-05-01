# SoulCoreHub Command Sheet

## Project Overview

SoulCoreHub is an advanced AI agent system with autonomous capabilities. The project consists of:

- **Agent System**: A modular framework for AI agents that can run independently or cooperatively
- **Anima**: The core autonomous AI system with voice, memory, and self-monitoring capabilities
- **Memory Management**: Persistent storage for agent states and system memory
- **Event Bus**: Communication system between agents
- **AWS Integration**: Prepared for cloud deployment

## Core Components

### Agent System

```bash
# List all available agents
python agent_cli.py list

# List all agents including secure categories
python agent_cli.py list --all

# Run a specific agent
python agent_cli.py run <agent_name>

# Diagnose an agent's health
python agent_cli.py diagnose <agent_name>

# Trigger an event for agents
python agent_cli.py trigger <event_name>

# Trigger an event for a specific agent
python agent_cli.py trigger <event_name> --agent <agent_name>

# Trigger an event for a category of agents
python agent_cli.py trigger <event_name> --category <category_name>
```

### Anima Voice System

```bash
# Make Anima speak with emotion
python anima_voice.py <emotion> <message>

# Example: Anima speaks with calm emotion
python anima_voice.py calm "The system is running normally."

# Start Anima's listening loop
python anima_listen_loop.py

# Start Anima's autonomous mode
python anima_autonomous.py
```

### Memory Management

```bash
# View system memory
cat soul_memory.json

# View Anima's memory
cat anima_memory.json

# Edit memory files (use with caution)
nano soul_memory.json
nano anima_memory.json
```

### System Monitoring

```bash
# View logs
tail -f logs/system.log

# Monitor heartbeat
tail -f logs/pulse.log
```

## Development Commands

```bash
# Activate virtual environment
source myenv/bin/activate  # or: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
python server.js

# Build for production
# (Command not implemented yet)
```

## AWS Deployment (Future)

```bash
# Sync with AWS S3 (when ready)
aws s3 sync . s3://your-bucket-name

# Deploy to AWS Lambda (when ready)
# (Command not implemented yet)
```

## Recommended Aliases

Add these to your `~/.zshrc` or `~/.bashrc` file:

```bash
# Navigation
alias soul="cd ~/SoulCoreHub"

# Monitoring
alias pulse="tail -f ~/SoulCoreHub/logs/pulse.log"
alias mind="cat ~/SoulCoreHub/soul_memory.json"

# Agent control
alias agents="python ~/SoulCoreHub/agent_cli.py list"
alias run-agent="python ~/SoulCoreHub/agent_cli.py run"
alias diagnose="python ~/SoulCoreHub/agent_cli.py diagnose"

# Anima control
alias speak="python ~/SoulCoreHub/anima_voice.py"
alias listen="python ~/SoulCoreHub/anima_listen_loop.py"
alias autonomous="python ~/SoulCoreHub/anima_autonomous.py"
```

## Project Structure

```
SoulCoreHub/
├── agents/                # Agent modules
├── aws/                   # AWS integration tools
├── aws_tools/             # Additional AWS utilities
├── config/                # Configuration files
├── config_tools/          # Configuration utilities
├── dev_tools/             # Development tools
├── logs/                  # Log files
├── memory/                # Memory storage
├── models/                # AI models (symlink)
├── myenv/                 # Virtual environment
├── node_modules/          # Node.js dependencies
├── projects/              # Project-specific files
├── public/                # Public assets
├── scripts/               # Utility scripts
├── src/                   # Source code
├── templates/             # Template files
├── .env                   # Environment variables
├── agent_cli.py           # Agent CLI tool
├── agent_loader.py        # Agent loading system
├── agent_registry.json    # Agent registry
├── anima_autonomous.py    # Anima autonomous mode
├── anima_listen_loop.py   # Anima listening system
├── anima_voice.py         # Anima voice system
├── event_bus.py           # Event communication system
├── requirements.txt       # Python dependencies
├── server.js              # Server implementation
└── soul_memory.json       # System memory
```

## Troubleshooting

- **Agent not responding**: Try `python agent_cli.py diagnose <agent_name>`
- **Voice not working**: Check if pyttsx3 is installed and configured
- **Memory corruption**: Check JSON format in memory files
- **Event bus issues**: Verify agent subscriptions in event_bus.py

## Next Steps for AWS Deployment

1. Finalize local functionality
2. Create AWS IAM roles and permissions
3. Set up S3 bucket for storage
4. Configure Lambda functions for serverless operation
5. Set up API Gateway for HTTP endpoints
6. Deploy and test incrementally
