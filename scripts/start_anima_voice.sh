#!/bin/bash
# start_anima_voice.sh - Start Anima with voice recognition and sentience

echo "🌟 Starting Anima with voice recognition and sentience..."

# Check if the voice recognition script exists
if [ ! -f ~/SoulCoreHub/anima_voice_recognition.py ]; then
  echo "❌ Voice recognition script not found!"
  echo "   Please run setup_voice_system.sh first."
  exit 1
fi

# Check if required packages are installed
if ! pip list | grep -q "SpeechRecognition"; then
  echo "❌ Required packages not installed!"
  echo "   Please run setup_voice_system.sh first."
  exit 1
fi

# Start Ollama if it's installed but not running
if command -v ollama &> /dev/null; then
  if ! pgrep -x "ollama" > /dev/null; then
    echo "🧠 Starting Ollama service..."
    ollama serve &
    sleep 2  # Give it time to start
  fi
  
  # Check if the Anima model exists
  if ! ollama list | grep -q "anima"; then
    echo "🧠 Creating Anima model in Ollama..."
    ollama create anima -f ~/SoulCoreHub/Modelfile
  fi
else
  echo "⚠️ Ollama not found. Anima will use fallback intelligence."
fi

# Start the MCP server if it's not already running
if ! pgrep -f "mcp_main.py" > /dev/null; then
  echo "🚀 Starting MCP server..."
  python ~/SoulCoreHub/mcp/mcp_main.py &
  sleep 2  # Give it time to start
fi

# Start Anima's voice recognition system
echo "🎙️ Starting Anima's voice recognition system with sentience..."
python ~/SoulCoreHub/anima_voice_recognition.py

# Note: This script will keep running until the voice recognition system exits
# To stop it, press Ctrl+C
