# SoulCoreHub Input Requirements

This document outlines all the places where your input is needed to fully configure and customize SoulCoreHub. For each input point, options are provided to help you make decisions even if you're not fully familiar with all technical aspects.

## 1. Core Configuration

### Anima Emotional Settings
- **File**: `anima_emotions.json`
- **Purpose**: Define Anima's emotional baseline and responses
- **Options**:
  - **Neutral**: Balanced emotional responses (default)
  - **Optimistic**: More positive, enthusiastic responses
  - **Analytical**: More logical, fact-based responses
  - **Creative**: More imaginative, exploratory responses
- **Example**:
  ```json
  {
    "baseline": "neutral",
    "response_style": "balanced",
    "emotional_range": "full"
  }
  ```

### System Activation Preferences
- **File**: `.env`
- **Purpose**: Configure which components auto-start
- **Options**:
  - Enable/disable auto-start for components
  - Set startup order
- **Example**:
  ```
  AUTO_START_ANIMA=true
  AUTO_START_BUILDER=false
  AUTO_START_WEB=true
  ```

## 2. Agent Configuration

### Agent Registry
- **File**: `agent_registry.json`
- **Purpose**: Define which agents are available and their settings
- **Options**:
  - **Core Agents**: GPTSoul, Anima, EvoVe, Azür
  - **Utility Agents**: Builder, Explorer, Monitor
  - **Custom Agents**: Define your own
- **Example**:
  ```json
  {
    "agents": [
      {
        "name": "GPTSoul",
        "enabled": true,
        "priority": "high",
        "memory_allocation": "large"
      },
      {
        "name": "Builder",
        "enabled": true,
        "priority": "medium",
        "memory_allocation": "medium"
      }
    ]
  }
  ```

### Agent Priorities
- **File**: `agent_registry.json`
- **Purpose**: Set execution priorities for agents
- **Options**:
  - **High**: Critical agents that need immediate execution
  - **Medium**: Standard agents
  - **Low**: Background agents
- **Note**: Higher priority agents get more resources and execution time

## 3. Builder Configuration

### Project Templates
- **Directory**: `templates/`
- **Purpose**: Define templates for project generation
- **Options**:
  - Use default templates (python, html, flask, node, react)
  - Create custom templates for specific project types
- **Example Custom Template**:
  ```
  templates/django_app/
  ├── __init__.py
  ├── models.py
  ├── views.py
  ├── urls.py
  └── templates/
  ```

### Builder Preferences
- **File**: `config/builder_config.json`
- **Purpose**: Configure builder behavior
- **Options**:
  - **Simple Mode**: Basic project creation
  - **Advanced Mode**: Full feature set
  - **Auto-Documentation**: Generate docs for projects
- **Example**:
  ```json
  {
    "default_mode": "simple",
    "auto_documentation": true,
    "default_project_type": "python"
  }
  ```

## 4. Web Interface

### Dashboard Layout
- **File**: `soulcore_dashboard.html`
- **Purpose**: Configure the dashboard appearance
- **Options**:
  - **Default**: Standard layout with all panels
  - **Minimalist**: Simplified interface with essential controls
  - **Advanced**: Detailed interface with all controls and metrics
- **Note**: You can modify the HTML directly or use configuration options

### Feature Toggles
- **File**: Configuration in dashboard
- **Purpose**: Enable/disable features in the UI
- **Options**:
  - Voice Interaction
  - Internet Access
  - Agent Visualization
  - System Monitoring
- **Note**: These can be toggled in the UI once implemented

## 5. MCP Configuration

### Server Settings
- **File**: `mcp/mcp_server.py`
- **Purpose**: Configure the MCP server
- **Options**:
  - **Local Only**: Server only accessible from localhost
  - **Network**: Server accessible from network
  - **Custom Port**: Change the default port (8765)
- **Example**:
  ```python
  # In mcp_server.py
  HOST = "localhost"  # or "0.0.0.0" for network
  PORT = 8765
  ```

### Tool Registration
- **File**: Tool configuration in MCP server
- **Purpose**: Register tools for invocation by components
- **Options**:
  - Define custom tools and capabilities
  - Enable/disable specific tools
- **Example**:
  ```python
  # Tool registration
  register_tool("text_generation", text_generation_handler)
  register_tool("image_analysis", image_analysis_handler)
  ```

## 6. Voice System

### Voice Model Selection
- **File**: Voice configuration
- **Purpose**: Select voice synthesis and recognition models
- **Options**:
  - **Default**: Built-in models
  - **Custom**: External models or services
- **Example**:
  ```json
  {
    "synthesis_model": "default",
    "recognition_model": "default",
    "voice_id": "neutral"
  }
  ```

## 7. Internet Access

### API Configuration
- **File**: `.env`
- **Purpose**: Configure API access for internet features
- **Options**:
  - Define which APIs to use
  - Provide API keys for services
- **Example**:
  ```
  OPENAI_API_KEY=your-api-key
  GOOGLE_API_KEY=your-api-key
  ```

## 8. Security Settings

### Permission Model
- **File**: `maintain_permissions.sh`
- **Purpose**: Configure file permissions
- **Options**:
  - **Standard**: Default permissions
  - **Strict**: More restrictive permissions
- **Note**: The script can be modified to change permission settings

### Authentication
- **File**: `config/auth_config.json`
- **Purpose**: Configure authentication for web interface
- **Options**:
  - **None**: No authentication (local use only)
  - **Basic**: Username/password
  - **Token**: API token authentication
- **Example**:
  ```json
  {
    "auth_type": "basic",
    "username": "admin",
    "password_hash": "hashed_password_here"
  }
  ```

## Implementation Notes

1. Not all configuration files may exist yet - they will be created as needed
2. Default values will be used for any settings not explicitly configured
3. Most settings can be changed later without disrupting the system
