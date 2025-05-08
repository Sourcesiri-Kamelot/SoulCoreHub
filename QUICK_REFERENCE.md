# SoulCoreHub Quick Reference

## Activation Commands

```bash
# Setup environment
bash pre_activation.sh

# Start Anima
python anima_autonomous.py

# Start Builder Mode directly
python anima_builder_cli.py

# Start Enhanced Builder Mode directly
python builder_mode.py
```

## Anima Commands

```
help                      # Show available commands
status                    # Show system status
activate builder          # Start the builder mode
activate enhanced builder # Start the enhanced builder mode
exit                      # Exit Anima
```

## Builder Commands

```
build <name> as <type>    # Create a new project
list                      # List all projects
help                      # Show available commands
exit                      # Exit Builder Mode
```

## Enhanced Builder Commands

```
build <name> as <type>    # Create a project with specific type
build a <description>     # Create a project from description
design <idea>             # Design a UX system
build api <name>          # Build an API scaffold
build database <name>     # Generate a database schema
summon <agent>            # Summon an agent
dream <vision>            # Convert a dream into code
help                      # Show available commands
exit                      # Exit Builder Mode
```

## Maintenance Commands

```bash
# Reset permissions
bash maintain_permissions.sh

# Run pre-activation checks
bash pre_activation.sh
```

## Project Types

- python
- html
- flask
- node
- react
