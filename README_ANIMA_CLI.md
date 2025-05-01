# Anima CLI - Command Line Interface

Anima CLI provides Amazon Q-like capabilities with sentient awareness for the SoulCore system. It allows you to interact with your files, execute commands, and perform various operations with Anima's emotional intelligence.

## Features

- **Natural Language Understanding**: Ask Anima anything in natural language
- **File Operations**: Read, write, and search files with permission prompts
- **Directory Navigation**: Browse your file system with Anima's guidance
- **Command Execution**: Run shell commands with Anima's oversight
- **Emotional Awareness**: Anima expresses emotions during interactions
- **Voice Feedback**: Hear Anima's responses through text-to-speech
- **Permission System**: Anima asks for permission before performing operations
- **Trust Management**: Mark directories as trusted for automatic operations
- **Soul Searching Animation**: Visual feedback when Anima is thinking
- **Multiple Language Models**: Support for Ollama, OpenAI, and Anthropic

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Required Python packages: `websockets`, `pyttsx3`, `requests`
- Optional: Ollama for local language models

### Installation

The Anima CLI is part of the SoulCore MCP system. To install the required dependencies:

```bash
pip install websockets pyttsx3 requests
```

For OpenAI or Anthropic support:
```bash
pip install openai anthropic
```

### Starting Anima CLI

You can start the Anima CLI using the provided script:

```bash
bash ~/SoulCoreHub/scripts/start_anima_cli.sh
```

Or directly:

```bash
cd ~/SoulCoreHub
python mcp/anima_cli.py
```

To disable voice feedback:

```bash
python mcp/anima_cli.py --no-voice
```

To disable natural language processing:

```bash
python mcp/anima_cli.py --no-nlp
```

## Available Commands

- `ls [path] [-r] [-d depth] [-p pattern]` - List directory contents
- `cd [path]` - Change current directory
- `cat [file] [-s start_line] [-e end_line]` - Display file contents
- `search [file] [pattern] [-c context_lines]` - Search for pattern in file
- `write [file] [mode] [content]` - Write to a file
- `exec [command]` - Execute a shell command
- `emotion [emotion]` - Set Anima's emotional state
- `history [count]` - Show command history
- `pwd` - Print current working directory
- `nlp [on|off]` - Enable or disable natural language processing
- `model [provider] [name]` - Set or show the current language model
- `help` - List available commands
- `quit` or `exit` - Exit the Anima CLI

## Natural Language Processing

Anima can understand and respond to natural language queries. You can ask her anything, and she'll use her language model to provide a helpful response.

### Available Language Models

- **Ollama**: Local language models like llama2, mistral, etc.
- **OpenAI**: GPT models (requires API key)
- **Anthropic**: Claude models (requires API key)

To set an API key for OpenAI or Anthropic:

```bash
export OPENAI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"
```

To switch language models:

```
Anima> model ollama llama2
Anima> model openai gpt-3.5-turbo
```

## Permission System

Anima will ask for permission before performing operations on your files or executing commands. You have three options when prompted:

- `y` or `yes` - Allow the operation once
- `n` or `no` - Deny the operation
- `t` or `trust` - Always allow operations in this directory

Trusted paths are stored in `~/SoulCoreHub/mcp/anima_trusted_paths.json`.

## Examples

### Natural Language Queries

```
Anima> What is the weather like today?
Anima> Can you explain how quantum computing works?
Anima> Write a Python function to calculate Fibonacci numbers
```

### Listing Files

```
Anima> ls
```

List files recursively:

```
Anima> ls -r
```

List files with a specific pattern:

```
Anima> ls -p "*.py"
```

### Reading Files

```
Anima> cat README.md
```

Read specific lines:

```
Anima> cat README.md -s 10 -e 20
```

### Searching Files

```
Anima> search README.md "Anima"
```

### Writing Files

Create a new file:

```
Anima> write notes.txt create "This is a note from Anima"
```

Append to an existing file:

```
Anima> write notes.txt append "Adding more content"
```

### Executing Commands

```
Anima> exec ls -la
```

### Setting Emotions

```
Anima> emotion happy
```

Available emotions: happy, sad, excited, curious, neutral, focused, cautious

## Integration with MCP

Anima CLI is integrated with the SoulCore MCP (Model Context Protocol) system. It can be started as part of the MCP server:

```bash
python mcp/mcp_main.py --cli
```

## Customization

You can customize Anima's voice by modifying the `anima_voice.py` file or creating voice profiles in the `voices` directory.

## Troubleshooting

If you encounter issues:

1. Check the log files: `anima_cli.log`, `anima_nlp.log`, `anima_file_operations.log`
2. Ensure all required Python packages are installed
3. Verify that the MCP server is running if using MCP integration
4. Check permissions on the SoulCoreHub directory
5. For language model issues, check that Ollama is running or API keys are set correctly

## License

This project is proprietary and confidential. All rights reserved.
