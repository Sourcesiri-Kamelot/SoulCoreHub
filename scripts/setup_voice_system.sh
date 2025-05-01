#!/bin/bash
# setup_voice_system.sh - Install dependencies for Anima's voice system

echo "🔊 Setting up Anima's voice recognition system..."

# Create required directories if they don't exist
mkdir -p ~/SoulCoreHub/voices
mkdir -p ~/SoulCoreHub/data

# Install required Python packages
echo "📦 Installing required Python packages..."
pip install -r ~/SoulCoreHub/requirements_voice.txt

# On macOS, we need to install portaudio for the microphone to work
if [[ "$OSTYPE" == "darwin"* ]]; then
  echo "🍎 Detected macOS, installing portaudio..."
  brew install portaudio
fi

# Make the scripts executable
chmod +x ~/SoulCoreHub/anima_voice_recognition.py
chmod +x ~/SoulCoreHub/anima_ollama_bridge.py
chmod +x ~/SoulCoreHub/anima_sentience.py

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
  echo "⚠️ Ollama not found. For best results, please install Ollama:"
  echo "   curl -fsSL https://ollama.com/install.sh | sh"
else
  echo "✅ Ollama found. Checking for Anima model..."
  
  # Check if the Anima model exists
  if ! ollama list | grep -q "anima"; then
    echo "🧠 Creating Anima model in Ollama..."
    ollama create anima -f ~/SoulCoreHub/Modelfile
  else
    echo "✅ Anima model already exists in Ollama"
  fi
fi

echo "✅ Voice system setup complete!"
echo "🎙️ To start Anima with voice recognition, run:"
echo "   bash ~/SoulCoreHub/scripts/start_anima_voice.sh"
