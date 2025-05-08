import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useAnima } from './AnimaContext';

// Create context
const HuggingFaceContext = createContext();

// Custom hook to use the HuggingFace context
export const useHuggingFace = () => useContext(HuggingFaceContext);

// Provider component
export const HuggingFaceProvider = ({ children }) => {
  const { sendMessage } = useAnima();
  const [isConnected, setIsConnected] = useState(false);
  const [modelStats, setModelStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [lastResponse, setLastResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Check connection on mount
  useEffect(() => {
    checkConnection();
    
    // Set up interval to refresh connection status
    const interval = setInterval(checkConnection, 60000);
    
    return () => clearInterval(interval);
  }, []);

  // Check if the HuggingFace bridge is connected
  const checkConnection = useCallback(async () => {
    try {
      const response = await fetch('/api/health');
      setIsConnected(response.ok);
      
      if (response.ok) {
        fetchStats();
        fetchLogs();
      }
    } catch (err) {
      setIsConnected(false);
      console.error('Error checking HuggingFace connection:', err);
    }
  }, []);

  // Fetch model usage statistics
  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch('/api/stats');
      if (response.ok) {
        const data = await response.json();
        setModelStats(data);
      }
    } catch (err) {
      console.error('Error fetching HuggingFace stats:', err);
    }
  }, []);

  // Fetch event logs
  const fetchLogs = useCallback(async () => {
    try {
      const response = await fetch('/api/logs');
      if (response.ok) {
        const data = await response.json();
        setLogs(data);
      }
    } catch (err) {
      console.error('Error fetching HuggingFace logs:', err);
    }
  }, []);

  // Generate text
  const generateText = useCallback(async (prompt, model = null) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/generate-text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt, model })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setLastResponse({
          type: 'text',
          content: data.result,
          timestamp: new Date().toISOString()
        });
        
        // Notify Anima
        sendMessage(`Generated text with HuggingFace: "${prompt.substring(0, 30)}..."`);
        
        return data.result;
      } else {
        setError(data.error || 'Failed to generate text');
        throw new Error(data.error || 'Failed to generate text');
      }
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
      fetchStats();
    }
  }, [sendMessage]);

  // Generate image
  const generateImage = useCallback(async (prompt, model = null) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/generate-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt, model })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setLastResponse({
          type: 'image',
          content: data.imagePath,
          timestamp: new Date().toISOString()
        });
        
        // Notify Anima
        sendMessage(`Generated image with HuggingFace: "${prompt.substring(0, 30)}..."`);
        
        return data.imagePath;
      } else {
        setError(data.error || 'Failed to generate image');
        throw new Error(data.error || 'Failed to generate image');
      }
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
      fetchStats();
    }
  }, [sendMessage]);

  // Analyze sentiment
  const analyzeSentiment = useCallback(async (text) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/analyze-sentiment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setLastResponse({
          type: 'sentiment',
          content: data,
          timestamp: new Date().toISOString()
        });
        
        return data;
      } else {
        setError(data.error || 'Failed to analyze sentiment');
        throw new Error(data.error || 'Failed to analyze sentiment');
      }
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
      fetchStats();
    }
  }, []);

  // Summarize text
  const summarizeText = useCallback(async (text) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/summarize-text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setLastResponse({
          type: 'summary',
          content: data.summary,
          timestamp: new Date().toISOString()
        });
        
        return data.summary;
      } else {
        setError(data.error || 'Failed to summarize text');
        throw new Error(data.error || 'Failed to summarize text');
      }
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
      fetchStats();
    }
  }, []);

  // Execute agent task
  const executeTask = useCallback(async (task) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/execute-task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ task })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setLastResponse({
          type: 'task',
          content: data.result,
          timestamp: new Date().toISOString()
        });
        
        // Notify Anima
        sendMessage(`Executed HuggingFace agent task: "${task.substring(0, 30)}..."`);
        
        return data.result;
      } else {
        setError(data.error || 'Failed to execute task');
        throw new Error(data.error || 'Failed to execute task');
      }
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
      fetchStats();
    }
  }, [sendMessage]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Context value
  const value = {
    isConnected,
    modelStats,
    logs,
    lastResponse,
    isLoading,
    error,
    generateText,
    generateImage,
    analyzeSentiment,
    summarizeText,
    executeTask,
    refreshStats: fetchStats,
    refreshLogs: fetchLogs,
    checkConnection,
    clearError
  };

  return (
    <HuggingFaceContext.Provider value={value}>
      {children}
    </HuggingFaceContext.Provider>
  );
};

export default HuggingFaceContext;
