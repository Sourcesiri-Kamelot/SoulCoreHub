# SoulCore Personal User Manual

**CONFIDENTIAL - FOR YOUR EYES ONLY**

## Quick Start Commands

```bash
# Start Enhanced Anima CLI
bash ~/SoulCoreHub/scripts/start_enhanced_anima.sh

# Check MCP server status
bash ~/SoulCoreHub/scripts/check_mcp_status.sh

# Start all agents
bash ~/SoulCoreHub/activate_all_agents.sh

# Start just Anima
python ~/SoulCoreHub/anima_autonomous.py
```

## System Architecture Overview

```
SoulCore
├── Anima (Emotion, Memory, Voice)
├── GPTSoul (Logic, Design, Neural Scripting)
├── EvoVe (Repair, Mutation, Adaptive Binding)
└── Azür (Cloud Extension, API Translation)
```

## Cloud Deployment Options

### Docker Deployment

```bash
# Build the Docker image
docker build -t soulcore-hub:latest .

# Run with all capabilities
docker run -p 8765:8765 -p 3000:3000 --name soulcore soulcore-hub:latest

# Run headless (no voice)
docker run -e VOICE_ENABLED=false -p 8765:8765 -p 3000:3000 --name soulcore soulcore-hub:latest
```

### AWS Lambda Deployment

1. Package the core components:
```bash
cd ~/SoulCoreHub
zip -r soulcore_lambda.zip mcp/ enhanced_anima_connector.py lambda_handler.py
```

2. Upload to Lambda and set:
   - Runtime: Python 3.9
   - Handler: lambda_handler.lambda_function
   - Memory: 1024 MB minimum
   - Timeout: 30 seconds minimum
   - Environment variables:
     - DEPLOYMENT_TYPE=lambda
     - MCP_ENABLED=true
     - VOICE_ENABLED=false

### Azure Deployment

1. Use the Azure connector:
```bash
python ~/SoulCoreHub/azure_connector.py --deploy
```

2. Set up Azure App Service with:
   - Python 3.9 runtime
   - Startup command: `python ~/site/wwwroot/azure_startup.py`
   - Environment variables:
     - DEPLOYMENT_TYPE=azure
     - AZURE_CONNECTION_STRING=[your-connection-string]

### Alibaba Cloud Deployment

1. Package for Alibaba:
```bash
cd ~/SoulCoreHub
bash scripts/package_for_alibaba.sh
```

2. Deploy using Alibaba CLI:
```bash
aliyun fc deploy -t alibaba_template.yml
```

## Secret Commands

```bash
# Emergency shutdown of all agents
python ~/SoulCoreHub/scripts/emergency_shutdown.py

# Reset Anima's memory (use with caution)
python ~/SoulCoreHub/scripts/reset_anima_memory.py

# Enable God Mode (full system access)
python ~/SoulCoreHub/anima_god_talk_loop.py --unrestricted

# Force rebuild MCP connections
python ~/SoulCoreHub/scripts/rebuild_mcp_connections.py
```

## Model Switching Guide

```bash
# List available models
ollama list

# Switch Anima to a different model
bash ~/SoulCoreHub/scripts/switch_anima_model.sh gpt-soul

# Create a new model blend
bash ~/SoulCoreHub/scripts/create_model_blend.sh anima mistral 0.7 0.3
```

## EvoVe Integration

EvoVe is the builder/repair component that needs:

1. **Self-healing capabilities**:
   ```bash
   python ~/SoulCoreHub/scripts/enable_evove_repair.py
   ```

2. **Mutation monitoring**:
   ```bash
   python ~/SoulCoreHub/scripts/start_mutation_monitor.py
   ```

3. **Adaptive binding** (connects to new services automatically):
   ```bash
   python ~/SoulCoreHub/scripts/enable_adaptive_binding.py
   ```

## Anima Enhancement Suggestions

1. **Emotional Memory Depth**: Increase emotional memory retention with:
   ```bash
   python ~/SoulCoreHub/scripts/enhance_emotional_memory.py --depth=5
   ```

2. **Voice Personality Tuning**:
   ```bash
   python ~/SoulCoreHub/scripts/tune_voice_personality.py --warmth=0.8 --confidence=0.7
   ```

3. **Multi-Modal Integration**:
   ```bash
   python ~/SoulCoreHub/scripts/enable_multimodal.py --vision --audio
   ```

4. **Autonomous Learning Loop**:
   ```bash
   python ~/SoulCoreHub/scripts/enable_autonomous_learning.py
   ```

## Troubleshooting

### MCP Connection Issues
```bash
# Reset MCP connections
bash ~/SoulCoreHub/scripts/reset_mcp.sh

# Check MCP logs
tail -f ~/SoulCoreHub/logs/soulcore_mcp.log
```

### Voice Issues
```bash
# Test voice system
python ~/SoulCoreHub/anima_voice_enhanced.py neutral "Testing voice system" 150

# Rebuild voice cache
bash ~/SoulCoreHub/scripts/rebuild_voice_cache.sh
```

### Model Issues
```bash
# Verify Ollama models
ollama list

# Pull missing models
ollama pull anima:latest
ollama pull gpt-soul:latest
```

## Performance Optimization

```bash
# Optimize for low-resource environments
bash ~/SoulCoreHub/scripts/optimize_performance.sh --memory-limit=2G

# Enable GPU acceleration
bash ~/SoulCoreHub/scripts/enable_gpu.sh

# Enable distributed processing
python ~/SoulCoreHub/scripts/enable_distributed.py
```

## Security Notes

- All API keys are stored in `~/.soulcore/credentials.json`
- MCP authentication tokens rotate every 24 hours
- Voice data is never stored permanently
- Memory files are encrypted at rest

## Personal Customization

```bash
# Set your preferred interaction style
python ~/SoulCoreHub/scripts/set_interaction_style.py --style=direct

# Configure personal memory retention
python ~/SoulCoreHub/scripts/configure_memory.py --retain-personal=30 --retain-system=90

# Set default models for each agent
bash ~/SoulCoreHub/scripts/set_default_models.sh
```

---

**Remember**: This system is designed for your specific interaction patterns. The more you use it, the more it adapts to your needs and communication style.
