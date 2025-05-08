# 🧠 SoulCoreHub Cheatsheet

## 🚀 Activation Sequence

```bash
# 1. Run pre-activation
bash pre_activation.sh

# 2. Start Anima
python anima_autonomous.py

# 3. From Anima, activate components:
activate builder
activate enhanced builder
```

## 🔧 Core Commands

### Anima
```
🧠 ANIMA> help                      # Show commands
🧠 ANIMA> status                    # System status
🧠 ANIMA> activate builder          # Start builder
🧠 ANIMA> activate enhanced builder # Start enhanced builder
🧠 ANIMA> exit                      # Exit
```

### Builder
```
builder> build myproject as python  # Create Python project
builder> list                       # List projects
builder> help                       # Show commands
builder> exit                       # Exit
```

### Enhanced Builder (Golem)
```
golem> build myapi as flask         # Create Flask project
golem> build a login app with auth  # Natural language build
golem> design user dashboard        # Design UX
golem> build api user-service       # Build API scaffold
golem> build database userdb        # Generate DB schema
golem> dream virtual assistant      # Convert dream to code
golem> help                         # Show commands
golem> exit                         # Exit
```

## 🛠️ Project Types

- `python` - Python script
- `flask` - Flask web app
- `html` - Static HTML site
- `node` - Node.js app
- `react` - React frontend

## 🔄 Maintenance

```bash
# Reset permissions
bash maintain_permissions.sh

# Fix environment
bash pre_activation.sh
```

## 📂 Directory Structure

```
SoulCoreHub/
├── anima_autonomous.py    # Anima core system
├── builder_mode.py        # Enhanced builder
├── anima_builder_cli.py   # Simple builder
├── pre_activation.sh      # Setup script
├── maintain_permissions.sh # Permission script
├── projects/              # Created projects
└── templates/             # Project templates
```

## 🔍 Troubleshooting

- If Anima crashes: Run `python anima_autonomous.py` again
- If builder fails: Check `projects` directory exists
- If permissions error: Run `bash maintain_permissions.sh`
- If MCP error: Ignore, non-critical for core functionality
