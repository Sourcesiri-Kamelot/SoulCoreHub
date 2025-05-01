#!/bin/bash
# Install dependencies for SoulCore MCP system

echo "Installing dependencies for SoulCore MCP system..."

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not found"
    exit 1
fi

# Install basic dependencies
echo "Installing basic dependencies..."
pip3 install websockets pyttsx3 requests

# Install NLP dependencies
echo "Installing NLP dependencies..."
pip3 install openai anthropic

# Install web scraping dependencies
echo "Installing web scraping dependencies..."
pip3 install beautifulsoup4

# Install optional dependencies
echo "Installing optional dependencies..."
pip3 install python-dotenv

echo "All dependencies installed successfully!"
echo "To use OpenAI or Anthropic APIs, set the following environment variables:"
echo "  export OPENAI_API_KEY=your_api_key"
echo "  export ANTHROPIC_API_KEY=your_api_key"
echo ""
echo "To use internet access features, set the following environment variables:"
echo "  export SERP_API_KEY=your_api_key"
echo "  export NEWSAPI_KEY=your_api_key"
echo "  export WEATHER_API_KEY=your_api_key"
echo ""
echo "Or create a config file at ~/SoulCoreHub/config/api_keys.json with these keys."
