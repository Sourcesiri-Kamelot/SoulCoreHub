# SoulCoreHub AutoHeal System

The AutoHeal system provides self-healing capabilities for failed toolchains in SoulCoreHub. It can automatically detect, diagnose, and repair common issues that might occur during operation.

## Features

- **Automatic Error Detection**: Identifies errors in toolchain execution
- **Error Diagnosis**: Analyzes errors and determines the root cause
- **Self-Healing**: Applies appropriate fixes based on the diagnosis
- **Backup and Restore**: Creates backups before healing to allow rollback if needed
- **Extensible**: Supports custom error patterns and healing strategies

## Components

### Core Components

- **AutoHealSystem** (`mcp/autoheal.py`): The main self-healing system
- **ToolchainError**: Custom exception class for toolchain errors
- **Repair Script** (`scripts/repair_toolchain.sh`): Command-line tool for manual repair
- **Health Check** (`scripts/check_mcp_health.sh`): Proactive system health monitoring
- **Test Script** (`test_autoheal.py`): Demonstrates the self-healing capabilities

### Healing Strategies

The AutoHeal system includes strategies for common issues:

1. **Missing Modules**: Automatically installs required Python modules
2. **Permission Issues**: Fixes file permissions for executables
3. **Syntax Errors**: Attempts to fix simple syntax errors in code
4. **Connection Errors**: Restarts services when connections fail
5. **File Not Found**: Creates missing files and directories
6. **JSON Format Errors**: Repairs malformed JSON configuration files
7. **Import Errors**: Fixes import statements in Python modules
8. **WebSocket Errors**: Restarts WebSocket connections

## Usage

### Automatic Healing

The AutoHeal system is integrated with the MCP server and client. When an error occurs during toolchain execution, it will:

1. Detect the error
2. Diagnose the root cause
3. Apply the appropriate healing strategy (if auto-approve is enabled)
4. Log the healing action

### Manual Repair

To manually check and repair toolchains:

```bash
# Basic repair check
./scripts/repair_toolchain.sh

# Auto-approve all healing actions
./scripts/repair_toolchain.sh --yes

# Repair a specific tool
./scripts/repair_toolchain.sh --tool model_router
```

### Health Check

To proactively check system health:

```bash
./scripts/check_mcp_health.sh
```

### Testing

To test the self-healing capabilities:

```bash
python test_autoheal.py
```

## Integration with EvoVe

The AutoHeal system is a core component of EvoVe's repair capabilities. EvoVe uses this system to:

1. Monitor the health of all toolchains
2. Detect failures in real-time
3. Apply self-healing strategies
4. Learn from successful repairs to improve future healing

## Configuration

Custom error patterns can be defined in `config/autoheal_patterns.json`:

```json
{
  "CustomError": {
    "pattern": "regex_pattern_to_match",
    "solution": "healing_strategy_name",
    "description": "Description of the error"
  }
}
```

## Logs and Backups

- **Logs**: Healing logs are stored in `logs/autoheal/`
- **Backups**: Backups created before healing are stored in `backups/autoheal/`

## Example: Healing a Failed Connection

When a connection to the MCP server fails:

1. The error is detected: `ConnectionError: Cannot connect to localhost:8765`
2. The AutoHeal system diagnoses it as a connection error
3. The healing strategy restarts the MCP server
4. The connection is restored

## Example: Fixing Permission Issues

When a script lacks execute permissions:

1. The error is detected: `PermissionError: [Errno 13] Permission denied`
2. The AutoHeal system diagnoses it as a permission error
3. The healing strategy applies execute permissions to the file
4. The script can now be executed
