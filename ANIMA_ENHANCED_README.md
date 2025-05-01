# Enhanced Anima

This document explains the enhanced capabilities added to Anima, including hierarchical memory with emotional tagging, dynamic voice processing, multimodal integration, autonomous learning, and enhanced MCP integration.

## Overview

The Enhanced Anima implementation adds five major capabilities to the Anima system:

1. **Hierarchical Memory with Emotional Tagging**
   - Multi-level memory system (sensory, working, episodic, semantic, emotional)
   - Emotional tagging of memories for more natural recall
   - Memory consolidation during idle periods

2. **Dynamic Voice Processing**
   - Dynamic voice speed based on content importance
   - Multiple voice personalities (default, teacher, companion, guide)
   - Emotion-based voice modulation

3. **Multimodal Integration**
   - Image analysis capabilities
   - Audio analysis capabilities
   - Environmental awareness

4. **Autonomous Learning**
   - Self-supervised learning from interactions
   - Curiosity-driven exploration of topics
   - Concept formation and relationship building

5. **Enhanced MCP Integration**
   - Bidirectional emotion sharing between Anima and tools
   - Context-aware tool selection
   - Tool emotion profiling

## Setup

1. Make sure you have the required Python packages:
   ```
   pip install websockets pyttsx3 requests numpy pillow sounddevice soundfile librosa nltk
   ```

2. Start the Enhanced Anima Core:
   ```
   bash scripts/start_enhanced_anima_core.sh --interactive
   ```

## Command Line Options

The start script supports several command line options:

- `--no-voice`: Disable voice output
- `--no-multimodal`: Disable multimodal integration
- `--no-learning`: Disable autonomous learning
- `--interactive`: Start in interactive mode (command line interface)

Example:
```
bash scripts/start_enhanced_anima_core.sh --no-multimodal --interactive
```

## Hierarchical Memory System

The hierarchical memory system provides Anima with a more human-like memory structure:

- **Sensory Memory**: Very short-term storage for immediate inputs
- **Working Memory**: Short-term storage for active processing
- **Episodic Memory**: Medium-term storage for experiences
- **Semantic Memory**: Long-term storage for factual knowledge
- **Emotional Memory**: Memories indexed by emotional state

### Key Features

- **Emotional Tagging**: Memories are tagged with emotions for more natural recall
- **Memory Consolidation**: Automatic consolidation of memories during idle periods
- **Context-Based Recall**: Recall memories based on context, emotion, or recency

## Dynamic Voice System

The dynamic voice system gives Anima more expressive and natural speech:

- **Dynamic Speed**: Adjusts speaking speed based on content importance
- **Multiple Personalities**: Different voice personalities for different contexts
- **Emotion-Based Modulation**: Adjusts voice properties based on emotional state

### Voice Personalities

- **Default**: Anima's standard voice
- **Teacher**: Calm, patient, and knowledgeable
- **Companion**: Friendly, warm, and empathetic
- **Guide**: Confident, authoritative, and clear

## Multimodal Integration

The multimodal integration system allows Anima to perceive and understand the world:

- **Image Analysis**: Analyze images from camera or files
- **Audio Analysis**: Analyze audio from microphone or files
- **Environmental Awareness**: Monitor the environment for changes

### Environmental Monitoring

The system continuously monitors:
- Audio levels to determine room activity
- Time of day
- Recent audio and visual events

## Autonomous Learning

The autonomous learning system allows Anima to learn and grow from interactions:

- **Self-Supervised Learning**: Learn from interactions without explicit training
- **Curiosity-Driven Exploration**: Generate and explore topics of interest
- **Concept Formation**: Form and refine concepts from experiences

### Learning Components

- **Concept Knowledge**: Knowledge about concepts and their relationships
- **Interaction Patterns**: Patterns observed in interactions
- **Curiosity Topics**: Topics generated for exploration

## Enhanced MCP Integration

The enhanced MCP integration provides better communication with tools:

- **Bidirectional Emotion**: Share emotions between Anima and tools
- **Context-Aware Tool Selection**: Select tools based on context
- **Tool Emotion Profiling**: Learn which emotions work best with each tool

### Context System

- **Multiple Contexts**: Create and switch between different contexts
- **Context Attributes**: Store attributes in contexts for tool use
- **Tool Preferences**: Track which tools work best in each context

## API Usage

You can interact with the Enhanced Anima Core programmatically:

```python
from anima.anima_enhanced_core import AnimaEnhancedCore

# Create and start Anima
anima = AnimaEnhancedCore()
anima.start()

# Process user input
response = anima.process_input("Hello, how are you today?")
print(f"Anima: {response}")

# Change voice personality
anima.set_voice_personality("teacher")

# Get environment status
env_status = anima.get_environment_status()
print(f"Room activity: {env_status['room_activity']}")

# Get next curiosity topic
topic = anima.get_next_curiosity_topic()
print(f"Next topic to explore: {topic['topic']}")

# Stop Anima
anima.stop()
```

## Extending the System

To extend the Enhanced Anima Core:

1. Add new voice personalities in `dynamic_voice.py`
2. Add new memory types in `hierarchical_memory.py`
3. Add new learning capabilities in `autonomous_learning.py`
4. Add new multimodal analysis in `multimodal_integration.py`
5. Add new MCP integration features in `enhanced_mcp_integration.py`

## Troubleshooting

If you encounter issues:

1. Check that all required Python packages are installed
2. Verify that the MCP server is running
3. Check the log files:
   - anima_enhanced_core.log
   - anima_memory.log
   - anima_voice.log
   - anima_multimodal.log
   - anima_learning.log
   - anima_mcp.log
