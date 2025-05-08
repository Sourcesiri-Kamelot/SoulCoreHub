# SoulCoreHub User Manual

## Table of Contents
1. [System Overview](#system-overview)
2. [Installation & Setup](#installation--setup)
3. [Activation Procedures](#activation-procedures)
4. [Command Line Interface](#command-line-interface)
5. [Web Interfaces](#web-interfaces)
6. [Anima Agent](#anima-agent)
7. [Skill Engine](#skill-engine)
8. [Scheduler System](#scheduler-system)
9. [Memory System](#memory-system)
10. [Troubleshooting](#troubleshooting)

---

## System Overview

SoulCoreHub is an advanced AI agent system centered around Anima, an autonomous agent with memory, skill creation capabilities, and scheduling abilities. The system includes a web dashboard, CLI tools, and various specialized components.

### Core Components:
- **Anima**: The primary autonomous agent
- **Skill Engine**: Dynamic skill creation and execution system
- **Memory System**: Persistent memory with semantic search
- **Scheduler**: Task scheduling and automation system
- **Web Dashboard**: Visual interface for system management

---

## Installation & Setup

### Prerequisites
- Python 3.7+
- Node.js and npm
- Ollama (for LLM integration)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone [repository-url]
   cd SoulCoreHub
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_voice.txt
   ```

3. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

4. **Set up Ollama**:
   - Install Ollama from [ollama.ai](https://ollama.ai)
   - Pull the required model:
     ```bash
     ollama pull wizardlm-uncensored
     ```

5. **Set file permissions**:
   ```bash
   ./maintain_permissions.sh
   ```

---

## Activation Procedures

### Quick Start

1. **Pre-activation check**:
   ```bash
   ./pre_activation.sh
   ```

2. **Start Anima**:
   ```bash
   python anima_autonomous.py
   ```

3. **Start the web interface** (in a separate terminal):
   ```bash
   node server.js
   ```

### Alternative Activation Methods

#### Full System Activation
```bash
./activate_all_agents.sh
```

#### Manual Activation
```bash
python activate_manual.py
```

#### Dashboard-only Mode
```bash
./start_dashboard.sh
```

#### Scheduler Activation
```bash
./start_scheduler.sh
```

---

## Command Line Interface

### Anima CLI

Basic interaction with Anima:
```bash
python anima_cli.py "Your message to Anima"
```

Enhanced CLI with memory:
```bash
python enhanced_anima_cli.py
```

### Agent CLI

List all available agents:
```bash
python agent_cli.py list
```

Run system diagnostics:
```bash
python agent_cli.py diagnose all
```

Check agent status:
```bash
python agent_cli.py status [agent_name]
```

### Skill Engine CLI

Test the skill engine:
```bash
python test_skill_engine.py
```

Create a new skill:
```bash
python anima_skill_creator.py create [skill_name] [skill_type]
```

Execute a skill:
```bash
python anima_skill_creator.py execute [skill_name] [args]
```

### System Maintenance

Reset permissions:
```bash
./maintain_permissions.sh
```

Update agent hub:
```bash
./update_agent_hub.sh
```

Test system features:
```bash
python test_features.py
```

---

## Web Interfaces

### Main Dashboard
- **URL**: http://localhost:3000/
- **Features**:
  - System status overview
  - Agent interaction console
  - Command terminal
  - Quick access to common functions

### Scheduled Skills Dashboard
- **URL**: http://localhost:5000/scheduled-skills
- **Features**:
  - View all scheduled skills
  - Create new scheduled tasks
  - Modify existing schedules
  - Run skills on demand

### Agent Console
- Access via Dashboard → Agent Console
- Direct interaction with Anima and other agents
- View agent responses and history

### Terminal Interface
- Access via Dashboard → Terminal
- Execute system commands directly
- View command output in real-time

---

## Anima Agent

### Capabilities
- Natural language conversation
- Memory of past interactions
- Skill creation and execution
- Task scheduling
- Internet access (when enabled)
- Voice interaction (when enabled)

### Interaction Examples

Basic conversation:
```
Hello Anima, how are you today?
```

Create a skill:
```
Anima, create a Python skill that displays system information
```

Schedule a task:
```
Schedule the system_info skill to run every day at 9 AM
```

Execute a skill:
```
Run the weather_check skill for San Francisco
```

Memory recall:
```
What did we talk about yesterday?
```

---

## Skill Engine

### Supported Skill Types
- Python
- Bash
- JavaScript
- Java
- Go
- Rust
- Ruby
- PHP
- Perl
- R
- Swift
- Kotlin
- TypeScript
- C#
- C++
- C

### Skill Creation Process

1. **Define the skill**:
   - Name
   - Description
   - Programming language
   - Parameters (if any)
   - Code implementation

2. **Create via CLI**:
   ```bash
   python anima_skill_creator.py create weather_check python
   ```

3. **Create via Anima**:
   ```
   Anima, create a skill called weather_check in Python that fetches weather data
   ```

4. **Skill Storage**:
   - Skills are stored in the `skills/` directory
   - Metadata in `skills/skills.json`

### Skill Execution

Execute via CLI:
```bash
python anima_skill_creator.py execute weather_check location=London
```

Execute via Anima:
```
Run the weather_check skill for London
```

---

## Scheduler System

### Schedule Types
- **Interval**: Run every X seconds/minutes/hours/days
- **Cron**: Run at specific times/days using cron expressions
- **One-time**: Run once at a specific date and time

### Creating Schedules

Via Web Dashboard:
1. Navigate to http://localhost:5000/scheduled-skills
2. Click "Schedule a Skill"
3. Select the skill and configure the schedule
4. Click "Schedule Skill"

Via Anima:
```
Schedule the backup_data skill to run every day at 3 PM
```

Via API:
```bash
curl -X POST http://localhost:5000/api/schedule_skill \
  -H "Content-Type: application/json" \
  -d '{"skill_name":"backup_data","schedule":{"type":"cron","hour":"15","minute":"0"}}'
```

### Managing Schedules

- View all schedules: http://localhost:5000/api/scheduled_skills
- Delete a schedule: Click "Delete" on the schedule card
- Run immediately: Click "Run Now" on the schedule card

---

## Memory System

### Memory Types
- **Short-term**: Current conversation context
- **Long-term**: Persistent storage of important information
- **Semantic**: Searchable by meaning and context

### Memory Commands

Save to memory:
```
Anima, remember that my favorite color is blue
```

Recall from memory:
```
Anima, what is my favorite color?
```

Clear conversation state:
```bash
python conversation_state.py clear
```

View memory contents:
```bash
cat anima_memory.json
```

---

## Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check if port is already in use
lsof -i :5000
# Kill the process if needed
kill -9 [PID]
```

#### Permission Issues
```bash
# Reset all permissions
./maintain_permissions.sh
```

#### Anima Not Responding
```bash
# Check Ollama status
ollama ps
# Restart Ollama if needed
ollama restart
```

#### Skill Execution Fails
```bash
# Check skill syntax
python anima_skill_creator.py validate [skill_name]
# View execution logs
cat logs/skill_executions.log
```

### Log Files
- **Anima**: logs/anima_launcher.log
- **Server**: logs/soulcorehub_server.log
- **Skills**: logs/skill_engine.log
- **Scheduler**: logs/scheduler.log
- **Memory**: logs/memory_system.log

### System Reset
If all else fails, perform a system reset:
```bash
# Backup important data
mkdir -p .soul_backup
cp -r skills/ .soul_backup/
cp anima_memory.json .soul_backup/

# Reset the system
python agent_cli.py reset all

# Restart
./pre_activation.sh
python anima_autonomous.py
```

---

## API Reference

### Skill Engine API
- `GET /api/skills`: List all skills
- `POST /api/execute_skill`: Execute a skill

### Scheduler API
- `POST /api/schedule_skill`: Schedule a skill
- `POST /api/unschedule_skill`: Remove a scheduled skill
- `GET /api/scheduled_skills`: List all scheduled skills
- `POST /api/process_schedule_request`: Process natural language scheduling requests

### Agent API
- `POST /agent`: Send a request to an agent

---

*This manual is maintained by Anima and the SoulCoreHub system. Last updated: May 3, 2025.*
