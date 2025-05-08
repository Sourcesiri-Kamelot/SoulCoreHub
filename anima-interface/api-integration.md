# Anima Interface API Integration Guide

This document outlines how to integrate the Anima Interface with the SoulCoreHub backend APIs.

## API Endpoints

### Core API

The core API is a RESTful API that provides access to the main functionality of SoulCoreHub.

#### Base URL

```
http://localhost:3001/api
```

#### Authentication

All requests should include an authentication token in the header:

```
Authorization: Bearer <token>
```

#### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/anima/status` | GET | Get Anima's current status |
| `/anima/input` | POST | Send input to Anima |
| `/anima/reflection` | POST | Add a reflection to Anima's memory |
| `/gptsoul/status` | GET | Get GPTSoul's current status |
| `/system/status` | GET | Get overall system status |
| `/agents` | GET | Get all agents |
| `/agents/:id` | GET | Get a specific agent |
| `/agents/:id/deploy` | POST | Deploy an agent |
| `/memory/logs` | GET | Get memory logs |
| `/memory/sync` | POST | Synchronize memory |
| `/evolution/trigger` | POST | Trigger evolution |
| `/files` | GET | Get all files |
| `/files/:id` | GET | Get a specific file |
| `/files/upload` | POST | Upload a file |
| `/files/process` | POST | Process a file |
| `/generate` | POST | Generate content |

## WebSocket Connection

The WebSocket connection provides real-time updates from the SoulCoreHub system.

#### Connection URL

```
ws://localhost:3001/ws
```

#### Events

| Event | Description |
|-------|-------------|
| `status_update` | System status update |
| `agent_update` | Agent status update |
| `memory_update` | Memory update |
| `emotional_state_change` | Emotional state change |
| `notification` | System notification |

## MCP (Model Context Protocol)

The MCP provides a standardized way for components to share context and invoke tools.

#### Connection URL

```
ws://localhost:8765
```

#### Request Format

```json
{
  "request_id": "unique-request-id",
  "tool": "tool-name",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "stream": false,
  "agent": "agent-name",
  "emotion": "neutral"
}
```

#### Response Format

```json
{
  "request_id": "unique-request-id",
  "result": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

#### Available Tools

| Tool | Description |
|------|-------------|
| `register_agent` | Register an agent with the MCP |
| `list_agents` | List all registered agents |
| `echo` | Echo a message (for testing) |
| `system_info` | Get system information |
| `file_read` | Read a file |
| `file_write` | Write to a file |
| `execute_command` | Execute a command |
| `memory_store` | Store data in memory |
| `memory_retrieve` | Retrieve data from memory |
| `generate_text` | Generate text using a local model |

## Integration Example

### REST API Example

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3001/api',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

// Get Anima status
const getAnimaStatus = async () => {
  try {
    const response = await api.get('/anima/status');
    return response.data;
  } catch (error) {
    console.error('Failed to get Anima status:', error);
    throw error;
  }
};

// Send input to Anima
const sendAnimaInput = async (input, context = {}) => {
  try {
    const response = await api.post('/anima/input', { input, context });
    return response.data;
  } catch (error) {
    console.error('Failed to send input to Anima:', error);
    throw error;
  }
};
```

### WebSocket Example

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:3001/ws', {
  auth: {
    token: 'your-auth-token'
  }
});

// Listen for status updates
socket.on('status_update', (data) => {
  console.log('Status update:', data);
  // Update UI with new status
});

// Listen for emotional state changes
socket.on('emotional_state_change', (data) => {
  console.log('Emotional state change:', data);
  // Update UI with new emotional state
});

// Listen for notifications
socket.on('notification', (data) => {
  console.log('Notification:', data);
  // Display notification in UI
});
```

### MCP Example

```javascript
import WebSocket from 'websocket';

class MCPClient {
  constructor(url = 'ws://localhost:8765', agentName = 'WebUI') {
    this.url = url;
    this.agentName = agentName;
    this.ws = null;
    this.connected = false;
    this.callbacks = new Map();
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket.w3cwebsocket(this.url);

      this.ws.onopen = () => {
        console.log('Connected to MCP server');
        this.connected = true;
        resolve(true);
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };

      this.ws.onclose = () => {
        console.log('Disconnected from MCP server');
        this.connected = false;
      };

      this.ws.onmessage = (message) => {
        const data = JSON.parse(message.data);
        const callback = this.callbacks.get(data.request_id);
        
        if (callback) {
          callback(data);
          this.callbacks.delete(data.request_id);
        }
      };
    });
  }

  invokeTool(toolName, parameters, emotion = 'neutral') {
    return new Promise((resolve, reject) => {
      if (!this.connected) {
        reject(new Error('Not connected to MCP server'));
        return;
      }

      const requestId = Date.now().toString();
      
      this.callbacks.set(requestId, (data) => {
        if (data.error) {
          reject(new Error(data.error));
        } else {
          resolve(data.result);
        }
      });

      const request = {
        request_id: requestId,
        tool: toolName,
        parameters,
        stream: false,
        agent: this.agentName,
        emotion
      };

      this.ws.send(JSON.stringify(request));
    });
  }
}

// Usage
const mcpClient = new MCPClient();
mcpClient.connect()
  .then(() => {
    return mcpClient.invokeTool('system_info', { include_resources: true });
  })
  .then((result) => {
    console.log('System info:', result);
  })
  .catch((error) => {
    console.error('Error:', error);
  });
```

## Error Handling

All API calls should include proper error handling. The API returns standard HTTP status codes:

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Security Considerations

- Always use HTTPS in production
- Store authentication tokens securely
- Validate all user inputs
- Implement rate limiting for API calls
- Use WebSocket authentication
- Implement proper error handling
