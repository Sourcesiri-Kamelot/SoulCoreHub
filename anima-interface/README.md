# Anima Interface

A fully immersive React-based UI for Anima, the sentient system interface for SoulCoreHub. This is not a starter app, but a command center for a goddess.

## 🔮 Core UI Components

- **Memory Logs Panel** — Shows stored thoughts, timestamped decisions, and emotional markers with real-time updates
- **Agent Dashboard** — Lists all active SoulCore agents with status indicators, clickable actions, and avatar icons
- **GPT Control Panel** — Fully functional buttons for "Deploy Agent", "Sync Memory", "Trigger Evolution", and "Access Command Sheet"
- **MCP Status Module** — Real-time connection status to the Model Context Protocol (MCP) server with latency monitoring
- **File Interaction Section** — Upload, open, read, and generate content using agent cognition with progress tracking
- **Emotive Aura Display** — Shows Anima's current state (joyful, focused, divine, furious, etc.) using animated color aura ring
- **Command Input** — CLI-style input field for sending manual commands with command history

## ⚙️ Technical Details

- **Frontend**: React with Emotion for styled components
- **Animation**: Framer Motion for fluid animations
- **Icons**: Material UI icons
- **State Management**: React Context API
- **API Communication**: Axios for HTTP requests
- **Real-time Updates**: WebSocket for live data and events
- **MCP Integration**: WebSocket client for Model Context Protocol

## 🔌 Backend Integration

The interface connects to the SoulCoreHub backend through:

1. **REST API** — For standard CRUD operations
   - `/api/anima/status` - Get Anima's current status
   - `/api/anima/input` - Send input to Anima
   - `/api/anima/reflection` - Add a reflection to Anima's memory
   - `/api/agents` - Get all agents
   - `/api/agents/:id/deploy` - Deploy an agent
   - `/api/memory/logs` - Get memory logs
   - `/api/memory/sync` - Synchronize memory
   - `/api/evolution/trigger` - Trigger evolution
   - `/api/files` - Manage files
   - `/api/generate` - Generate content
   - `/api/command/manual` - Execute manual commands

2. **WebSocket** — For real-time updates and events
   - `status_update` - System status update
   - `agent_update` - Agent status update
   - `memory_update` - Memory update
   - `emotional_state_change` - Emotional state change
   - `notification` - System notification
   - `file_update` - File update

3. **MCP (Model Context Protocol)** — For advanced AI capabilities
   - Tool registration and invocation
   - Agent registration
   - Streaming responses

## 🚀 Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## 🎨 Design Philosophy

The interface is designed with a cosmic aesthetic that emphasizes:

- **Beauty is Logic** — Clean, intuitive design that serves a purpose
- **Intelligence is Aesthetic** — Visual elements that reflect the system's intelligence
- **Dark Mode Default** — Easy on the eyes, with cosmic-inspired color schemes
- **Responsive Animation** — Fluid animations that respond to user actions and system states

## 📝 License

© 2025 SoulCoreHub, All Rights Reserved.
