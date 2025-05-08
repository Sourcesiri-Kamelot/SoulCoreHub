# SoulCoreHub Activation Guide

This guide provides step-by-step instructions for activating SoulCoreHub and its components.

## Quick Start

For a quick and safe activation of SoulCoreHub:

1. Run the pre-activation script:
   ```bash
   bash pre_activation.sh
   ```

2. Start Anima:
   ```bash
   python anima_autonomous.py
   ```

3. From within Anima, you can activate other components:
   ```
   activate builder
   ```
   or
   ```
   activate enhanced builder
   ```

## Component Activation

### Anima Core System

Anima is the emotional core and primary interface:

```bash
python anima_autonomous.py
```

Available commands within Anima:
- `help` - Show available commands
- `status` - Show system status
- `activate builder` - Start the builder mode
- `activate enhanced builder` - Start the enhanced builder mode
- `exit` - Exit Anima

### Builder Mode

The Builder Mode (simplified):

```bash
python anima_builder_cli.py
```

Available commands within Builder Mode:
- `build <name> as <type>` - Create a new project
- `list` - List all projects
- `help` - Show available commands
- `exit` - Exit Builder Mode

### Enhanced Builder Mode (Golem Engine)

The Enhanced Builder Mode with more capabilities:

```bash
python builder_mode.py
```

Available commands within Enhanced Builder Mode:
- `build <name> as <type>` - Create a project with specific type
- `build a <description>` - Create a project from description
- `design <idea>` - Design a UX system
- `build api <name>` - Build an API scaffold
- `build database <name>` - Generate a database schema
- `help` - Show available commands
- `exit` - Exit Builder Mode

## Troubleshooting

If you encounter permission issues:

```bash
bash maintain_permissions.sh
```

If components aren't loading properly:

```bash
bash pre_activation.sh
```

## System Requirements

- Python 3.6+
- Node.js (for web interface)
- Git (for version control features)

## Security Note

Remember to update your `.env` file with proper credentials and ensure it's not committed to version control.
