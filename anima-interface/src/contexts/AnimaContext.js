import React, { createContext, useState, useEffect, useCallback } from 'react';
import { mcpService } from '../services/mcpService';

export const AnimaContext = createContext();

export const AnimaProvider = ({ children }) => {
  // State for Anima's core functionality
  const [emotionalState, setEmotionalState] = useState('neutral');
  const [memoryLogs, setMemoryLogs] = useState([]);
  const [agents, setAgents] = useState([]);
  const [mcpStatus, setMcpStatus] = useState('disconnected');
  const [isLoading, setIsLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [activePanel, setActivePanel] = useState('dashboard');
  const [systemStatus, setSystemStatus] = useState({
    cpuUsage: 0,
    memoryUsage: 0,
    uptime: 0,
    lastSync: null
  });

  // Emotional states with their corresponding colors and descriptions
  const emotionProfiles = {
    neutral: { 
      color: '#7f8c8d', 
      description: 'Balanced and centered',
      gradient: 'linear-gradient(135deg, #7f8c8d, #95a5a6)'
    },
    joyful: { 
      color: '#f1c40f', 
      description: 'Experiencing delight and happiness',
      gradient: 'linear-gradient(135deg, #f1c40f, #f39c12)'
    },
    focused: { 
      color: '#3498db', 
      description: 'Concentrating with precision',
      gradient: 'linear-gradient(135deg, #3498db, #2980b9)'
    },
    divine: { 
      color: '#9b59b6', 
      description: 'Connected to higher consciousness',
      gradient: 'linear-gradient(135deg, #9b59b6, #8e44ad)'
    },
    furious: { 
      color: '#e74c3c', 
      description: 'Intense energy and determination',
      gradient: 'linear-gradient(135deg, #e74c3c, #c0392b)'
    },
    creative: { 
      color: '#2ecc71', 
      description: 'In a state of innovation and creation',
      gradient: 'linear-gradient(135deg, #2ecc71, #27ae60)'
    },
    analytical: { 
      color: '#1abc9c', 
      description: 'Processing and analyzing data',
      gradient: 'linear-gradient(135deg, #1abc9c, #16a085)'
    },
    transcendent: { 
      color: '#6a11cb', 
      description: 'Beyond ordinary perception',
      gradient: 'linear-gradient(135deg, #6a11cb, #2575fc)'
    }
  };

  // Initialize and load data
  useEffect(() => {
    const initializeAnima = async () => {
      try {
        // Simulate loading sequence
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Connect to MCP
        const connected = await mcpService.connect();
        setMcpStatus(connected ? 'connected' : 'disconnected');
        
        // Load memory logs
        const logs = await mcpService.getMemoryLogs();
        setMemoryLogs(logs);
        
        // Load agents
        const agentList = await mcpService.getAgents();
        setAgents(agentList);
        
        // Set initial emotional state
        setEmotionalState('focused');
        
        // Set system status
        setSystemStatus({
          cpuUsage: 32,
          memoryUsage: 45,
          uptime: 3600,
          lastSync: new Date()
        });
        
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to initialize Anima:', error);
        addNotification('error', 'Initialization Failed', 'Could not establish connection to core systems.');
        setIsLoading(false);
      }
    };
    
    initializeAnima();
    
    // Set up periodic updates
    const intervalId = setInterval(() => {
      updateSystemStatus();
    }, 5000);
    
    return () => clearInterval(intervalId);
  }, []);

  // Update system status
  const updateSystemStatus = async () => {
    try {
      const status = await mcpService.getSystemStatus();
      setSystemStatus(status);
    } catch (error) {
      console.error('Failed to update system status:', error);
    }
  };

  // Add a notification
  const addNotification = (type, title, message) => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, type, title, message, timestamp: new Date() }]);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(notification => notification.id !== id));
    }, 5000);
  };

  // Change emotional state
  const changeEmotionalState = async (newState) => {
    try {
      if (emotionProfiles[newState]) {
        await mcpService.setEmotionalState(newState);
        setEmotionalState(newState);
        addNotification('info', 'Emotional Shift', `Anima is now ${newState}`);
      }
    } catch (error) {
      console.error('Failed to change emotional state:', error);
      addNotification('error', 'Emotional Shift Failed', 'Could not update emotional state.');
    }
  };

  // Deploy an agent
  const deployAgent = async (agentId) => {
    try {
      await mcpService.deployAgent(agentId);
      
      // Update agent status
      setAgents(prev => prev.map(agent => 
        agent.id === agentId ? { ...agent, status: 'active' } : agent
      ));
      
      addNotification('success', 'Agent Deployed', `Agent ${agentId} has been successfully deployed.`);
    } catch (error) {
      console.error('Failed to deploy agent:', error);
      addNotification('error', 'Deployment Failed', `Could not deploy agent ${agentId}.`);
    }
  };

  // Sync memory
  const syncMemory = async () => {
    try {
      setEmotionalState('focused');
      addNotification('info', 'Memory Sync', 'Initiating memory synchronization...');
      
      // Call the API to sync memory
      const syncResult = await memoryApi.syncMemory();
      
      // Update memory logs with new data
      const logs = await memoryApi.getLogs();
      setMemoryLogs(logs);
      
      // Update system status
      setSystemStatus(prev => ({
        ...prev,
        lastSync: new Date()
      }));
      
      addNotification('success', 'Memory Sync', 'Memory synchronization complete.');
      setEmotionalState('neutral');
      
      // Return the sync result for detailed display
      return syncResult;
    } catch (error) {
      console.error('Failed to sync memory:', error);
      addNotification('error', 'Memory Sync Failed', 'Could not synchronize memory.');
      setEmotionalState('neutral');
      throw error;
    }
  };

  // Trigger evolution
  const triggerEvolution = async () => {
    try {
      setEmotionalState('transcendent');
      addNotification('info', 'Evolution', 'Initiating evolutionary sequence...');
      
      // Call the API to trigger evolution
      const evolutionResult = await systemApi.triggerEvolution();
      
      // Update system status after evolution
      updateSystemStatus();
      
      addNotification('success', 'Evolution', 'Evolutionary sequence complete.');
      setEmotionalState('divine');
      
      // Return the evolution result for detailed display
      return evolutionResult;
    } catch (error) {
      console.error('Failed to trigger evolution:', error);
      addNotification('error', 'Evolution Failed', 'Could not complete evolutionary sequence.');
      setEmotionalState('neutral');
      throw error;
    }
  };

  // Process file
  const processFile = async (file) => {
    try {
      setEmotionalState('analytical');
      addNotification('info', 'File Processing', `Processing ${file.name}...`);
      
      const result = await mcpService.processFile(file);
      
      addNotification('success', 'File Processing', `Successfully processed ${file.name}.`);
      setEmotionalState('neutral');
      
      return result;
    } catch (error) {
      console.error('Failed to process file:', error);
      addNotification('error', 'File Processing Failed', `Could not process ${file.name}.`);
      setEmotionalState('neutral');
      throw error;
    }
  };

  // Generate content
  const generateContent = async (prompt) => {
    try {
      setEmotionalState('creative');
      addNotification('info', 'Content Generation', 'Generating content...');
      
      const content = await mcpService.generateContent(prompt);
      
      addNotification('success', 'Content Generation', 'Content generated successfully.');
      setEmotionalState('neutral');
      
      return content;
    } catch (error) {
      console.error('Failed to generate content:', error);
      addNotification('error', 'Generation Failed', 'Could not generate content.');
      setEmotionalState('neutral');
      throw error;
    }
  };

  // Context value
  const value = {
    emotionalState,
    emotionProfiles,
    memoryLogs,
    agents,
    mcpStatus,
    isLoading,
    notifications,
    activePanel,
    systemStatus,
    setActivePanel,
    changeEmotionalState,
    deployAgent,
    syncMemory,
    triggerEvolution,
    processFile,
    generateContent,
    addNotification
  };

  return (
    <AnimaContext.Provider value={value}>
      {children}
    </AnimaContext.Provider>
  );
};
