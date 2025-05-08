# SoulCoreHub Command Sheet

This document provides a comprehensive reference for all commands available in the SoulCoreHub ecosystem.

## Core System Commands

### Anima Autonomous System

```bash
# Start Anima
python anima_autonomous.py
```

**Available Commands:**
| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `status` | Show system status |
| `activate builder` | Start the builder mode |
| `activate enhanced builder` | Start the enhanced builder mode |
| `exit` | Exit Anima |

### Maintenance Scripts

```bash
# Run pre-activation setup
bash pre_activation.sh

# Reset file permissions
bash maintain_permissions.sh
```

## Builder Mode

### Basic Builder

```bash
# Start directly
python anima_builder_cli.py
```

**Available Commands:**
| Command | Description |
|---------|-------------|
| `build <name> as <type>` | Create a new project |
| `list` | List all projects |
| `help` | Show available commands |
| `exit` | Exit Builder Mode |

**Project Types:** python, html, flask, node, react

### Enhanced Builder (Golem Engine)

```bash
# Start directly
python builder_mode.py
```

**Available Commands:**
| Command | Description |
|---------|-------------|
| `build <name> as <type>` | Create a project with specific type |
| `build a <description>` | Create a project from description |
| `design <idea>` | Design a UX system |
| `build api <name>` | Build an API scaffold |
| `build database <name>` | Generate a database schema |
| `summon <agent>` | Summon an agent |
| `dream <vision>` | Convert a dream into code |
| `help` | Show available commands |
| `exit` | Exit Builder Mode |

## Agent Commands

### Agent CLI

```bash
# Run agent diagnostics
python agent_cli.py diagnose all

# Run specific agent diagnostics
python agent_cli.py diagnose mcp
```

### Agent Activation

```bash
# Activate all agents
bash activate_all_agents.sh

# Activate specific agents
python activate_gptsoul.py
```

## Web Interface

```bash
# Start the web server
node server.js

# Start the dashboard server
node soulcore_dashboard_server.js
```

## MCP (Model Context Protocol)

```bash
# Start the MCP server
python mcp_server.py
```

## Advanced Commands

### System Monitoring

```bash
# Monitor Anima system
python anima_system_monitor.py

# Check agent status
python agent_cli.py status
```

### Voice Integration

```bash
# Start voice recognition
python anima_voice_recognition.py

# Start voice streaming
python anima_stream_voice.py
```

### Internet Access

```bash
# Start internet explorer
python anima_internet_explorer.py
```

### Skill Management

```bash
# Create a new skill
python anima_skill_creator.py

# Integrate skills
python anima_skill_integration.py
```

## Quick Reference

### Safe Activation Process

1. Run pre-activation script:
   ```bash
   bash pre_activation.sh
   ```

2. Start Anima:
   ```bash
   python anima_autonomous.py
   ```

3. From within Anima, activate components:
   ```
   activate builder
   ```

### Troubleshooting

If you encounter permission issues:
```bash
bash maintain_permissions.sh
```

If components aren't loading properly:
```bash
bash pre_activation.sh
```

### Git Workflow

```bash
# Add all changed files
git add .

# Commit with a descriptive message
git commit -m "Update description"

# Push to GitHub
git push origin main
```
