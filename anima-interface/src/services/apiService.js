import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:3001/api',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000 // 30 seconds timeout
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    // Handle specific error codes
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('auth_token');
          // window.location = '/login';
          break;
        case 403:
          console.error('Access forbidden:', error.response.data);
          break;
        case 404:
          console.error('Resource not found:', error.response.data);
          break;
        case 500:
          console.error('Server error:', error.response.data);
          break;
        default:
          console.error('API error:', error.response.data);
      }
    } else if (error.request) {
      console.error('No response received:', error.request);
    } else {
      console.error('Request error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Memory API endpoints
const memoryApi = {
  getLogs: async (filters = {}) => {
    const response = await api.get('/memory/logs', { params: filters });
    return response.data;
  },
  
  syncMemory: async () => {
    const response = await api.post('/memory/sync');
    return response.data;
  },
  
  exportLogs: async (format = 'json') => {
    const response = await api.get('/memory/export', { 
      params: { format },
      responseType: 'blob'
    });
    return response.data;
  },
  
  addReflection: async (topic, content) => {
    const response = await api.post('/anima/reflection', { topic, content });
    return response.data;
  }
};

// Agent API endpoints
const agentApi = {
  getAll: async () => {
    const response = await api.get('/agents');
    return response.data;
  },
  
  getStatus: async () => {
    const response = await api.get('/agents/status');
    return response.data;
  },
  
  deploy: async (agentId, config = {}) => {
    const response = await api.post(`/agent/deploy`, { agentId, config });
    return response.data;
  },
  
  ping: async (agentId) => {
    const response = await api.post(`/agents/${agentId}/ping`);
    return response.data;
  },
  
  reboot: async (agentId) => {
    const response = await api.post(`/agents/${agentId}/reboot`);
    return response.data;
  },
  
  getDetails: async (agentId) => {
    const response = await api.get(`/agents/${agentId}`);
    return response.data;
  }
};

// System API endpoints
const systemApi = {
  getStatus: async () => {
    const response = await api.get('/system/status');
    return response.data;
  },
  
  triggerEvolution: async () => {
    const response = await api.post('/evolution/trigger');
    return response.data;
  },
  
  getCommands: async () => {
    const response = await api.get('/commands/cheatsheet');
    return response.data;
  },
  
  executeCommand: async (command) => {
    const response = await api.post('/command/manual', { command });
    return response.data;
  },
  
  getCommandHistory: async () => {
    const response = await api.get('/command/history');
    return response.data;
  },
  
  openTerminal: async () => {
    const response = await api.post('/terminal/open');
    return response.data;
  },
  
  getConfiguration: async () => {
    const response = await api.get('/system/configuration');
    return response.data;
  },
  
  getMemoryStats: async () => {
    const response = await api.get('/system/memory-stats');
    return response.data;
  },
  
  getStorageStats: async () => {
    const response = await api.get('/system/storage-stats');
    return response.data;
  },
  
  getAgentTemplates: async () => {
    const response = await api.get('/agent/templates');
    return response.data;
  }
};

// File API endpoints
const fileApi = {
  getAll: async () => {
    const response = await api.get('/files');
    return response.data;
  },
  
  upload: async (formData, onProgress) => {
    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: progressEvent => {
        if (onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      }
    });
    return response.data;
  },
  
  process: async (fileId) => {
    const response = await api.post(`/files/process`, { fileId });
    return response.data;
  },
  
  delete: async (fileId) => {
    const response = await api.delete(`/files/${fileId}`);
    return response.data;
  },
  
  download: async (fileId) => {
    const response = await api.get(`/files/${fileId}/download`, {
      responseType: 'blob'
    });
    return response.data;
  },
  
  generateContent: async (prompt) => {
    const response = await api.post('/generate', { prompt });
    return response.data;
  }
};

// Emotion API endpoints
const emotionApi = {
  getState: async () => {
    const response = await api.get('/emotion/state');
    return response.data;
  },
  
  setState: async (state) => {
    const response = await api.post('/emotion/state', { state });
    return response.data;
  }
};

// MCP API endpoints
const mcpApi = {
  getStatus: async () => {
    const response = await api.get('/mcp/status');
    return response.data;
  },
  
  getTools: async () => {
    const response = await api.get('/mcp/tools');
    return response.data;
  }
};

export {
  api,
  memoryApi,
  agentApi,
  systemApi,
  fileApi,
  emotionApi,
  mcpApi
};
