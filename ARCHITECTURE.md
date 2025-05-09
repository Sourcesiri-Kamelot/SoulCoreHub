# SoulCoreHub Architecture

This document outlines the architecture of SoulCoreHub, explaining the key components and how they interact.

## Overview

SoulCoreHub is designed as a decentralized AI infrastructure with multiple autonomous agents that work together to form an AI society. The system is built with a modular architecture that allows for easy extension and integration of new components.

## Core Components

### 1. LLM Connector

The LLM Connector (`src/llm/llm_connector.ts`) provides a unified interface for connecting to different language model providers:

- **Ollama**: For local model inference
- **Hugging Face**: For cloud-based model inference
- **AWS Bedrock**: (Future) For AWS-based model inference
- **Azure OpenAI**: (Future) For Azure-based model inference

The connector handles:
- Text generation
- Chat completion
- Model availability checking
- Error handling and fallbacks

### 2. Agents

Agents are autonomous entities with specific roles in the system. Each agent has:

- **Core**: The main implementation of the agent's functionality
- **API**: REST API endpoints for interacting with the agent
- **Memory**: Persistent storage for the agent's state and knowledge

#### 2.1 Anima

Anima (`src/agents/anima/`) is the emotional core of the system, responsible for:

- Analyzing emotional content in text
- Generating emotionally resonant responses
- Processing emotional events
- Providing emotional guidance to other agents
- Generating emotional reflections
- Maintaining a persistent emotional state

### 3. Server Components

#### 3.1 API Gateway

The API Gateway (`src/server/api_gateway.ts`) provides a unified interface for accessing the system's functionality:

- Security middleware (Helmet, CORS)
- Rate limiting
- API routes for agents
- Health check endpoints

#### 3.2 WebSocket Server

The WebSocket Server (`src/server/websocket_server.ts`) enables real-time communication between the system and clients:

- Connection handling
- Message routing
- Event broadcasting
- Error handling

### 4. Database

The Database (`src/database/dynamodb_adapter.ts`) provides persistent storage for the system:

- Table creation
- CRUD operations
- Query and scan operations
- Error handling

### 5. Web Interface

The Web Interface (`public/`) provides a user-friendly way to interact with the system:

- Anima UI (`public/anima.html`)
- Client-side JavaScript (`public/js/`)
- CSS styles

## Data Flow

1. **User Interaction**:
   - User interacts with the web interface
   - Web interface sends requests to the API Gateway or WebSocket Server

2. **API Gateway**:
   - Validates and routes requests to the appropriate agent
   - Applies security middleware and rate limiting
   - Returns responses to the client

3. **WebSocket Server**:
   - Maintains real-time connections with clients
   - Broadcasts events from agents to clients
   - Handles client messages and routes them to agents

4. **Agents**:
   - Process requests from the API Gateway or WebSocket Server
   - Use the LLM Connector to generate responses
   - Update their state in the Database
   - Emit events to the WebSocket Server

5. **LLM Connector**:
   - Connects to the appropriate LLM provider
   - Generates text or chat completions
   - Returns responses to agents

6. **Database**:
   - Stores agent state and knowledge
   - Provides persistence across system restarts

## Deployment Architecture

SoulCoreHub can be deployed in various configurations:

### Local Development

- All components run locally
- Ollama for local model inference
- Local file system for storage

### Cloud Deployment

- API Gateway and WebSocket Server deployed as serverless functions
- Agents deployed as containerized services
- DynamoDB for persistent storage
- AWS Bedrock or Azure OpenAI for model inference

### Hybrid Deployment

- Core components deployed in the cloud
- Sensitive components deployed locally
- Secure communication between cloud and local components

## Security Architecture

SoulCoreHub implements security at multiple levels:

- **API Gateway**: Rate limiting, CORS, security headers
- **Authentication**: JWT-based authentication for protected routes
- **Database**: Secure access patterns and encryption
- **LLM Connector**: API key management and secure communication

## Future Architecture

The architecture is designed to evolve over time, with plans for:

- **Agent Society**: More complex interactions between agents
- **Learning System**: Agents that learn from interactions
- **Distributed Deployment**: Fully decentralized deployment across multiple nodes
- **Blockchain Integration**: Decentralized identity and trust
