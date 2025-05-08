# Anima Builder - Natural Language Development Interface

Anima Builder is a natural language interface for development tasks in Visual Studio Code and the terminal. It allows you to control your development environment using conversational commands.

## Features

- **Natural Language Commands**: Control VS Code and terminal using plain English
- **File Operations**: Create, edit, and manage files with natural language
- **Project Scaffolding**: Create new projects with a simple command
- **Terminal Integration**: Run terminal commands through natural language
- **VS Code Integration**: Control VS Code features and extensions

## Components

The Anima Builder system consists of several components:

1. **VS Code Bridge**: Connects Anima to VS Code
2. **Terminal Tool**: Executes terminal commands
3. **Builder Tool**: Creates and manages projects
4. **Natural Language Command Tool**: Parses natural language into structured commands
5. **Builder CLI**: Command-line interface for Anima Builder

## Installation

1. Ensure you have the MCP server running:
   ```bash
   python mcp/mcp_main.py
   ```

2. Register the tools with the MCP server:
   ```bash
   python -c "from mcp.tool_registry import get_registry; get_registry().load_tools_from_directory('tools')"
   ```

3. Start the VS Code bridge:
   ```bash
   python anima_vscode_bridge.py
   ```

## Usage

### Command Line Interface

You can use the Anima Builder CLI to execute natural language commands:

```bash
python anima_builder_cli.py "create a new file called hello.py with content print('Hello, world!')"
```

Or run it in interactive mode:

```bash
python anima_builder_cli.py -i
```

### Example Commands

Here are some example commands you can use:

- **Create a file**: "Create a new file called hello.py with content print('Hello, world!')"
- **Edit a file**: "Edit the file hello.py"
- **Run a terminal command**: "Run the command ls -la"
- **Create a project**: "Create a new Python project called myproject with description 'My awesome project'"
- **Install dependencies**: "Install the dependency requests"
