# SoulCoreHub Permission Management

This document outlines the permission management strategy for SoulCoreHub, implemented with the help of Amazon Q.

## Permission Changes

All tool permissions have been set to trusted (executable) for the following:

1. **Core Python Scripts**:
   - All Python files in the main directory
   - Agent implementation files
   - Configuration tools
   - Development utilities
   - AWS integration tools

2. **Shell Scripts**:
   - All shell scripts in the scripts directory

3. **Server**:
   - The Node.js server.js file

## Maintenance Scripts

Two maintenance scripts have been created:

### maintain_permissions.sh

This script ensures all necessary files have executable permissions. It can be run anytime permissions need to be reset:

```bash
bash /Users/helo.im.ai/SoulCoreHub/maintain_permissions.sh
```

### pre_activation.sh

This script performs pre-activation checks and sets up the environment before running a full SoulCoreHub activation:

```bash
bash /Users/helo.im.ai/SoulCoreHub/pre_activation.sh
```

## Safe Activation Process

To safely activate SoulCoreHub without crashing:

1. Run the pre-activation script:
   ```bash
   bash pre_activation.sh
   ```

2. Start the core system:
   ```bash
   python anima_autonomous.py
   ```

3. In a separate terminal, start the web interface:
   ```bash
   node server.js
   ```

## Git Workflow

Before activation, commit changes to GitHub:

```bash
# Add all changed files
git add .

# Commit with a descriptive message
git commit -m "Update tool permissions and add maintenance scripts"

# Push to GitHub
git push origin main
```

## Troubleshooting

If you encounter permission issues after a system update or git pull:

```bash
# Reset permissions
bash maintain_permissions.sh

# Check system status
python agent_cli.py diagnose all
```
