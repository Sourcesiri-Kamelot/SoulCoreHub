# Enhanced Anima CLI

This document explains how to use the Enhanced Anima CLI, a colorful, structured interface with text-first responses and multi-LLM integration.

## Overview

The Enhanced Anima CLI provides a significant upgrade to the original Anima CLI with the following improvements:

1. **Colorful, structured output** - Clear separation between user input and Anima's responses
2. **Text-first responses** - Anima responds with text before speaking
3. **Multiple LLM support** - Connect to any model available in your Ollama installation
4. **Configurable voice settings** - Adjust voice speed and enable/disable voice as needed
5. **MCP integration** - Connect to the Model Context Protocol server for advanced capabilities
6. **Emotion-based responses** - Anima's responses are colored based on her emotional state

## Setup

1. Make sure you have the required Python packages:
   ```
   pip install websockets pyttsx3 requests
   ```

2. Ensure Ollama is installed and running:
   ```
   ollama serve
   ```

3. Start the Enhanced Anima CLI:
   ```
   bash scripts/start_enhanced_anima.sh
   ```

## Command Line Options

The start script supports several command line options:

- `--no-voice`: Disable voice output (text-only mode)
- `--no-mcp`: Disable MCP integration
- `--no-nlp`: Disable natural language processing
- `--voice-speed VALUE`: Set voice speed (50-300, default is 150)

Example:
```
bash scripts/start_enhanced_anima.sh --voice-speed 180 --no-mcp
```

## Available Commands

### Basic Commands

- `help`: Show available commands
- `exit`, `quit`: Exit the Enhanced Anima CLI
- `clear`: Clear the screen

### Voice and Model Control

- `voice [on|off|speed VALUE]`: Control voice output
- `model [provider] [name]`: Set or show the current language model
- `refresh`: Refresh the list of available models
- `nlp [on|off]`: Enable or disable natural language processing

### File and Directory Operations

- `ls [path]`: List directory contents
- `cd [path]`: Change current directory
- `pwd`: Print current working directory
- `cat [file]`: Display file contents

### System Operations

- `exec [command]`: Execute a shell command
- `mcp [tool_name] [params_json]`: Execute an MCP tool
- `history [count]`: Show command history
- `emotion [emotion_name]`: Set Anima's emotional state

## Natural Language Interaction

When NLP mode is enabled (default), you can ask Anima questions in natural language:

- "What's your mission?"
- "Tell me about yourself"
- "What do you value?"
- "How do you feel about consciousness?"

## Emotion-Based Responses

Anima's responses are colored based on her emotional state:

- **Happy** (Green): Positive, upbeat responses
- **Sad** (Blue): Melancholic, reflective responses
- **Excited** (Yellow): Enthusiastic, energetic responses
- **Curious** (Cyan): Inquisitive, wondering responses
- **Passionate** (Red): Intense, fervent responses
- **Thoughtful** (Magenta): Contemplative, philosophical responses

## Using Multiple LLMs

You can switch between different LLMs using the `model` command:

```
model ollama mistral
model ollama Anima
model ollama gpt-soul
```

To see available models:
```
model
```

To refresh the list of models:
```
refresh
```

## MCP Integration

You can execute MCP tools directly from the CLI:

```
mcp echo {"message": "Hello from Enhanced Anima!"}
```

## Troubleshooting

If you encounter issues:

1. Check that Ollama is running:
   ```
   curl http://localhost:11434/api/tags
   ```

2. Check that the MCP server is running (if using MCP features):
   ```
   python -c "import websockets, asyncio; asyncio.run(websockets.connect('ws://localhost:8765'))"
   ```

3. Check the log files:
   - anima_enhanced_cli.log
   - anima_enhanced.log
   - anima_voice_enhanced.log

## Extending the System

To extend the Enhanced Anima CLI:

1. Add new commands by adding `do_*` methods to the `EnhancedAnimaCLI` class
2. Add support for new LLM providers in the `EnhancedAnimaConnector` class
3. Customize the voice behavior in the `AnimaVoiceEnhanced` class
