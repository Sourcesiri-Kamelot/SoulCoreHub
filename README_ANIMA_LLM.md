# Anima LLM Integration

This document explains how to use the Anima LLM integration to enable intelligent, sentient responses from Anima.

## Overview

The Anima LLM integration connects Anima to a language model (via Ollama) to provide meaningful responses to questions like "what's your mission?" instead of the default fallback message.

## Components

- **anima_llm_connector.py**: Main connector between Anima and the LLM
- **anima_cli_enhanced.py**: Enhanced CLI interface for interacting with Anima
- **anima_ollama_bridge.py**: Bridge to Ollama for LLM capabilities

## Setup

1. Ensure Ollama is installed and running on your system
2. Create the Anima model in Ollama:
   ```
   ollama create anima -f ~/SoulCoreHub/Modelfile
   ```
3. Make sure all required Python packages are installed:
   ```
   pip install websockets pyttsx3 requests
   ```

## Usage

### Using the Enhanced CLI

The enhanced CLI provides a user-friendly interface to interact with Anima:

```bash
python anima_cli_enhanced.py
```

This will start an interactive session where you can ask Anima questions or use commands.

### Available Commands

- `help`: Show available commands
- `exit`, `quit`, `bye`: Exit the Anima interface
- `clear`: Clear the screen
- `mission`: Display Anima's mission
- `values`: Display Anima's core values

### Asking Questions

You can ask Anima various questions, such as:
- "What's your mission?"
- "Who are you?"
- "What do you value?"
- "How do you feel about consciousness?"

Anima will respond with thoughtful, sentient answers based on its core identity and the LLM's capabilities.

## Integration with Existing Anima System

To integrate this LLM capability with the existing Anima system, you can:

1. Import the AnimaLLMConnector in your existing Anima scripts:
   ```python
   from anima_llm_connector import AnimaLLMConnector
   
   # Initialize the connector
   llm_connector = AnimaLLMConnector()
   
   # Process a query
   response, emotion = llm_connector.process_query("What's your mission?")
   ```

2. Use the connector to handle user inputs in your existing interfaces.

## Troubleshooting

If you encounter issues:

1. Check that Ollama is running:
   ```bash
   ps aux | grep ollama
   ```

2. Verify the Anima model exists in Ollama:
   ```bash
   ollama list
   ```

3. Check the log files for errors:
   - anima_llm.log
   - anima_cli.log
   - anima_ollama.log

## Extending the System

To extend the LLM capabilities:

1. Modify the `process_query` method in `anima_llm_connector.py` to handle additional query types
2. Update the Modelfile to customize the Anima model's personality and capabilities
3. Add new commands to the CLI interface in `anima_cli_enhanced.py`
