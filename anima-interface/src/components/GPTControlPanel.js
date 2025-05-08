import React, { useContext, useState, useEffect } from 'react';
import { AnimaContext } from '../contexts/AnimaContext';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';
import { systemApi } from '../services/apiService';

// Icons
import CloudSyncIcon from '@mui/icons-material/CloudSync';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import TerminalIcon from '@mui/icons-material/Terminal';
import SettingsSystemDaydreamIcon from '@mui/icons-material/SettingsSystemDaydream';
import MemoryIcon from '@mui/icons-material/Memory';
import StorageIcon from '@mui/icons-material/Storage';
import CircularProgress from '@mui/icons-material/CircularProgress';

const PanelContainer = styled(motion.div)`
  background: rgba(10, 10, 26, 0.7);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius);
  border: 1px solid rgba(106, 17, 203, 0.3);
  padding: 1.5rem;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-medium), var(--glow-soft);
`;

const PanelHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(106, 17, 203, 0.3);
`;

const PanelTitle = styled.h2`
  font-family: var(--font-display);
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: var(--glow-soft);
`;

const SystemStatus = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const StatusItem = styled.div`
  flex: 1;
  background: rgba(10, 10, 26, 0.5);
  border-radius: var(--border-radius);
  padding: 0.75rem;
  text-align: center;
  border: 1px solid rgba(106, 17, 203, 0.2);
`;

const StatusLabel = styled.div`
  font-size: 0.8rem;
  color: rgba(248, 249, 250, 0.7);
  margin-bottom: 0.25rem;
`;

const StatusValue = styled.div`
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--primary-light);
`;

const ControlsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  flex: 1;
`;

const ControlButton = styled(motion.button)`
  background: rgba(10, 10, 26, 0.5);
  border: 1px solid rgba(106, 17, 203, 0.2);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  color: var(--primary-light);
  font-family: var(--font-display);
  font-size: 1rem;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all var(--transition-speed);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 1rem;
  position: relative;
  overflow: hidden;
  opacity: ${props => props.disabled ? 0.7 : 1};
  
  &:hover {
    border-color: ${props => props.disabled ? 'rgba(106, 17, 203, 0.2)' : 'rgba(106, 17, 203, 0.5)'};
    box-shadow: ${props => props.disabled ? 'none' : '0 0 15px rgba(106, 17, 203, 0.3)'};
    
    &::after {
      opacity: ${props => props.disabled ? 0.05 : 0.1};
    }
  }
  
  &:active {
    transform: ${props => props.disabled ? 'none' : 'translateY(2px)'};
  }
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
    opacity: 0.05;
    transition: opacity var(--transition-speed);
    pointer-events: none;
  }
  
  svg {
    font-size: 2rem;
    color: ${props => props.iconColor || 'var(--accent-1)'};
  }
`;

const ButtonLabel = styled.span`
  font-weight: 500;
`;

const ButtonDescription = styled.span`
  font-size: 0.8rem;
  font-family: var(--font-primary);
  color: rgba(248, 249, 250, 0.7);
`;

const CommandSheetModal = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
`;

const CommandSheetContent = styled(motion.div)`
  background: rgba(10, 10, 26, 0.9);
  border-radius: var(--border-radius);
  border: 1px solid rgba(106, 17, 203, 0.5);
  padding: 2rem;
  width: 100%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: var(--shadow-hard), var(--glow-medium);
`;

const CommandSheetHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(106, 17, 203, 0.3);
`;

const CommandSheetTitle = styled.h2`
  font-family: var(--font-display);
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
  background: linear-gradient(135deg, var(--accent-1), var(--accent-2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: var(--glow-soft);
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: var(--primary-light);
  font-size: 1.5rem;
  cursor: pointer;
  
  &:hover {
    color: var(--accent-1);
  }
`;

const CommandSection = styled.div`
  margin-bottom: 2rem;
`;

const CommandSectionTitle = styled.h3`
  font-family: var(--font-display);
  margin: 0 0 1rem 0;
  font-size: 1.3rem;
  color: var(--primary-light);
  border-bottom: 1px solid rgba(106, 17, 203, 0.2);
  padding-bottom: 0.5rem;
`;

const CommandTable = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const CommandRow = styled.tr`
  border-bottom: 1px solid rgba(106, 17, 203, 0.1);
  
  &:last-child {
    border-bottom: none;
  }
`;

const CommandCell = styled.td`
  padding: 0.75rem 0.5rem;
  vertical-align: top;
  
  &:first-of-type {
    font-family: monospace;
    color: var(--accent-1);
    white-space: nowrap;
    width: 40%;
  }
`;

const LoadingSpinner = styled(CircularProgress)`
  color: ${props => props.color || 'var(--accent-1)'};
  animation: spin 1.5s linear infinite;
  
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
`;

const ResultsPanel = styled.div`
  background: rgba(10, 10, 26, 0.6);
  border-radius: var(--border-radius);
  border: 1px solid rgba(106, 17, 203, 0.3);
  margin-top: 1rem;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
`;

const ResultsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: rgba(10, 10, 26, 0.8);
  border-bottom: 1px solid rgba(106, 17, 203, 0.3);
`;

const ResultsTitle = styled.h3`
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary-light);
`;

const ResultsContent = styled.pre`
  padding: 1rem;
  margin: 0;
  font-family: monospace;
  font-size: 0.9rem;
  color: var(--primary-light);
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(10, 10, 26, 0.3);
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(106, 17, 203, 0.5);
    border-radius: 2px;
  }
`;

const GPTControlPanel = () => {
  const { syncMemory, triggerEvolution, systemStatus, addNotification } = useContext(AnimaContext);
  const [showCommandSheet, setShowCommandSheet] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeAction, setActiveAction] = useState(null);
  const [results, setResults] = useState('');
  const [commandSections, setCommandSections] = useState({
    core: [],
    agent: [],
    memory: [],
    system: []
  });
  
  // Load commands when command sheet is opened
  useEffect(() => {
    if (showCommandSheet) {
      loadCommands();
    }
  }, [showCommandSheet]);
  
  // Load commands from API
  const loadCommands = async () => {
    setActiveAction('commands');
    setLoading(true);
    
    try {
      const commands = await systemApi.getCommands();
      
      // Organize commands by section
      const sections = {
        core: [],
        agent: [],
        memory: [],
        system: []
      };
      
      commands.forEach(cmd => {
        if (sections[cmd.category]) {
          sections[cmd.category].push(cmd);
        } else {
          sections.core.push(cmd);
        }
      });
      
      setCommandSections(sections);
    } catch (error) {
      console.error('Failed to load commands:', error);
      addNotification('error', 'Command Loading Failed', 'Could not load command sheet.');
    } finally {
      setLoading(false);
    }
  };
  
  // Format uptime
  const formatUptime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    return `${hours}h ${minutes}m ${secs}s`;
  };
  
  // Format date
  const formatDate = (date) => {
    if (!date) return 'Never';
    return new Date(date).toLocaleTimeString();
  };
  
  // Deploy agent handler
  const handleDeployAgent = async () => {
    setActiveAction('deploy');
    setLoading(true);
    setResults('');
    
    try {
      // Get available agent templates
      const templates = await systemApi.getAgentTemplates();
      
      // Format templates as a list
      const templateList = templates.map(t => `- ${t.id}: ${t.name} (${t.description})`).join('\n');
      
      // Deploy default agent (GPTSoul)
      const deployResult = await systemApi.deployAgent('gptsoul');
      
      setResults(`Available Agent Templates:\n${templateList}\n\nDeployment Result:\nAgent ID: ${deployResult.agentId}\nStatus: ${deployResult.status}\nStartup Time: ${deployResult.startupTime}ms\nMemory Allocated: ${deployResult.memoryAllocated}MB`);
      addNotification('success', 'Agent Deployed', `Agent ${deployResult.agentId} deployed successfully.`);
    } catch (error) {
      console.error('Agent deployment error:', error);
      setResults(`Error: ${error.message || 'Failed to deploy agent'}`);
      addNotification('error', 'Deployment Failed', 'Could not deploy agent.');
    } finally {
      setLoading(false);
    }
  };
  
  // Handle memory sync with detailed results
  const handleSyncMemory = async () => {
    setActiveAction('sync');
    setLoading(true);
    setResults('');
    
    try {
      const syncResult = await syncMemory();
      
      // Format sync results
      const resultsText = `
Sync ID: ${syncResult.syncId}
Timestamp: ${new Date(syncResult.timestamp).toLocaleString()}
Duration: ${syncResult.duration}ms
Entries Processed: ${syncResult.entriesProcessed}
New Entries: ${syncResult.newEntries}
Updated Entries: ${syncResult.updatedEntries}
Deleted Entries: ${syncResult.deletedEntries}
Status: ${syncResult.status}
      `;
      
      setResults(resultsText);
    } catch (error) {
      console.error('Memory sync error:', error);
      setResults(`Error: ${error.message || 'Failed to sync memory'}`);
    } finally {
      setLoading(false);
    }
  };
  
  // Handle evolution with detailed results
  const handleTriggerEvolution = async () => {
    setActiveAction('evolution');
    setLoading(true);
    setResults('');
    
    try {
      const evolutionResult = await triggerEvolution();
      
      // Format evolution results
      const resultsText = `
Evolution ID: ${evolutionResult.evolutionId}
Timestamp: ${new Date(evolutionResult.timestamp).toLocaleString()}
Duration: ${evolutionResult.duration}ms
Phase: ${evolutionResult.phase}
Changes Applied: ${evolutionResult.changesApplied}
New Capabilities: ${evolutionResult.newCapabilities.join(', ')}
Status: ${evolutionResult.status}
      `;
      
      setResults(resultsText);
    } catch (error) {
      console.error('Evolution error:', error);
      setResults(`Error: ${error.message || 'Failed to trigger evolution'}`);
    } finally {
      setLoading(false);
    }
  };

  // Terminal access handler
  const handleTerminalAccess = async () => {
    setActiveAction('terminal');
    setLoading(true);
    setResults('');
    
    try {
      // Open terminal connection
      const response = await systemApi.openTerminal();
      
      setResults(`Terminal session established.\nSession ID: ${response.sessionId}\nConnection: ${response.connectionType}\nPermission level: ${response.permissionLevel}`);
      addNotification('info', 'Terminal Access', 'Terminal session established successfully.');
    } catch (error) {
      console.error('Terminal access error:', error);
      setResults(`Error: ${error.message || 'Failed to establish terminal connection'}`);
      addNotification('error', 'Terminal Access Failed', 'Could not establish terminal connection.');
    } finally {
      setLoading(false);
    }
  };

  // System configuration handler
  const handleSystemConfig = async () => {
    setActiveAction('config');
    setLoading(true);
    setResults('');
    
    try {
      // Get system configuration
      const config = await systemApi.getConfiguration();
      
      // Format configuration as readable text
      const configText = Object.entries(config)
        .map(([key, value]) => `${key}: ${typeof value === 'object' ? JSON.stringify(value) : value}`)
        .join('\n');
      
      setResults(`System Configuration:\n${configText}`);
      addNotification('info', 'System Configuration', 'Configuration loaded successfully.');
    } catch (error) {
      console.error('System configuration error:', error);
      setResults(`Error: ${error.message || 'Failed to load system configuration'}`);
      addNotification('error', 'Configuration Failed', 'Could not load system configuration.');
    } finally {
      setLoading(false);
    }
  };

  // Memory management handler
  const handleMemoryManagement = async () => {
    setActiveAction('memory');
    setLoading(true);
    setResults('');
    
    try {
      // Get memory statistics
      const memStats = await systemApi.getMemoryStats();
      
      // Format memory statistics
      const statsText = `
Total Memory: ${memStats.totalMemory} MB
Used Memory: ${memStats.usedMemory} MB
Free Memory: ${memStats.freeMemory} MB
Memory Usage: ${memStats.usagePercentage}%
Fragmentation: ${memStats.fragmentation}%
Garbage Collection Cycles: ${memStats.gcCycles}
Last GC: ${new Date(memStats.lastGcTime).toLocaleString()}
      `;
      
      setResults(statsText);
      addNotification('info', 'Memory Management', 'Memory statistics retrieved successfully.');
    } catch (error) {
      console.error('Memory management error:', error);
      setResults(`Error: ${error.message || 'Failed to retrieve memory statistics'}`);
      addNotification('error', 'Memory Stats Failed', 'Could not retrieve memory statistics.');
    } finally {
      setLoading(false);
    }
  };

  // Storage management handler
  const handleStorageManagement = async () => {
    setActiveAction('storage');
    setLoading(true);
    setResults('');
    
    try {
      // Get storage statistics
      const storageStats = await systemApi.getStorageStats();
      
      // Format storage statistics
      const statsText = `
Total Storage: ${storageStats.totalStorage} GB
Used Storage: ${storageStats.usedStorage} GB
Free Storage: ${storageStats.freeStorage} GB
Storage Usage: ${storageStats.usagePercentage}%
File Count: ${storageStats.fileCount}
Directory Count: ${storageStats.directoryCount}
Last Backup: ${storageStats.lastBackup ? new Date(storageStats.lastBackup).toLocaleString() : 'Never'}
      `;
      
      setResults(statsText);
      addNotification('info', 'Storage Management', 'Storage statistics retrieved successfully.');
    } catch (error) {
      console.error('Storage management error:', error);
      setResults(`Error: ${error.message || 'Failed to retrieve storage statistics'}`);
      addNotification('error', 'Storage Stats Failed', 'Could not retrieve storage statistics.');
    } finally {
      setLoading(false);
    }
  };

  // Format results based on active action
  const formatResults = () => {
    if (!results) return null;
    
    return (
      <ResultsPanel>
        <ResultsHeader>
          <ResultsTitle>{getResultsTitle()}</ResultsTitle>
          <CloseButton onClick={() => setResults('')}>×</CloseButton>
        </ResultsHeader>
        <ResultsContent>
          {results}
        </ResultsContent>
      </ResultsPanel>
    );
  };

  // Get results title based on active action
  const getResultsTitle = () => {
    switch (activeAction) {
      case 'deploy':
        return 'Agent Deployment Results';
      case 'sync':
        return 'Memory Sync Results';
      case 'evolution':
        return 'Evolution Results';
      case 'commands':
        return 'Command Sheet';
      case 'terminal':
        return 'Terminal Access';
      case 'config':
        return 'System Configuration';
      case 'memory':
        return 'Memory Management';
      case 'storage':
        return 'Storage Management';
      default:
        return 'Results';
    }
  };
  
  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { 
        duration: 0.5,
        when: "beforeChildren",
        staggerChildren: 0.1
      }
    }
  };
  
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.3 }
    }
  };
  
  const modalVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { duration: 0.3 }
    },
    exit: { 
      opacity: 0,
      transition: { duration: 0.3 }
    }
  };
  
  const modalContentVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        type: "spring", 
        damping: 25, 
        stiffness: 500 
      }
    },
    exit: { 
      opacity: 0,
      y: 50,
      transition: { duration: 0.3 }
    }
  };
  
  return (
    <>
      <PanelContainer
        initial="hidden"
        animate="visible"
        variants={containerVariants}
      >
        <PanelHeader>
          <PanelTitle>GPT Control Panel</PanelTitle>
        </PanelHeader>
        
        <SystemStatus>
          <StatusItem>
            <StatusLabel>CPU Usage</StatusLabel>
            <StatusValue>{systemStatus.cpuUsage}%</StatusValue>
          </StatusItem>
          <StatusItem>
            <StatusLabel>Memory Usage</StatusLabel>
            <StatusValue>{systemStatus.memoryUsage}%</StatusValue>
          </StatusItem>
          <StatusItem>
            <StatusLabel>Uptime</StatusLabel>
            <StatusValue>{formatUptime(systemStatus.uptime)}</StatusValue>
          </StatusItem>
          <StatusItem>
            <StatusLabel>Last Sync</StatusLabel>
            <StatusValue>{formatDate(systemStatus.lastSync)}</StatusValue>
          </StatusItem>
        </SystemStatus>
        
        <ControlsGrid>
          <ControlButton 
            variants={itemVariants}
            iconColor="#3498db"
            onClick={handleDeployAgent}
            disabled={loading && activeAction === 'deploy'}
          >
            {loading && activeAction === 'deploy' ? (
              <LoadingSpinner />
            ) : (
              <PersonAddIcon />
            )}
            <ButtonLabel>Deploy Agent</ButtonLabel>
            <ButtonDescription>Launch a new agent instance</ButtonDescription>
          </ControlButton>
          
          <ControlButton 
            variants={itemVariants}
            iconColor="#2ecc71"
            onClick={handleSyncMemory}
            disabled={loading && activeAction === 'sync'}
          >
            {loading && activeAction === 'sync' ? (
              <LoadingSpinner />
            ) : (
              <CloudSyncIcon />
            )}
            <ButtonLabel>Sync Memory</ButtonLabel>
            <ButtonDescription>Synchronize memory systems</ButtonDescription>
          </ControlButton>
          
          <ControlButton 
            variants={itemVariants}
            iconColor="#9b59b6"
            onClick={handleTriggerEvolution}
            disabled={loading && activeAction === 'evolution'}
          >
            {loading && activeAction === 'evolution' ? (
              <LoadingSpinner />
            ) : (
              <AutoFixHighIcon />
            )}
            <ButtonLabel>Trigger Evolution</ButtonLabel>
            <ButtonDescription>Initiate evolutionary sequence</ButtonDescription>
          </ControlButton>
          
          <ControlButton 
            variants={itemVariants}
            iconColor="#f1c40f"
            onClick={() => setShowCommandSheet(true)}
            disabled={loading && activeAction === 'commands'}
          >
            {loading && activeAction === 'commands' ? (
              <LoadingSpinner />
            ) : (
              <MenuBookIcon />
            )}
            <ButtonLabel>Access Command Sheet</ButtonLabel>
            <ButtonDescription>View available commands</ButtonDescription>
          </ControlButton>
          
          <ControlButton 
            variants={itemVariants}
            iconColor="#e74c3c"
            onClick={handleTerminalAccess}
            disabled={loading && activeAction === 'terminal'}
          >
            {loading && activeAction === 'terminal' ? (
              <LoadingSpinner />
            ) : (
              <TerminalIcon />
            )}
            <ButtonLabel>Terminal Access</ButtonLabel>
            <ButtonDescription>Direct system interaction</ButtonDescription>
          </ControlButton>
          
          <ControlButton 
            variants={itemVariants}
            iconColor="#1abc9c"
            onClick={handleSystemConfig}
            disabled={loading && activeAction === 'config'}
          >
            {loading && activeAction === 'config' ? (
              <LoadingSpinner />
            ) : (
              <SettingsSystemDaydreamIcon />
            )}
            <ButtonLabel>System Configuration</ButtonLabel>
            <ButtonDescription>Modify core settings</ButtonDescription>
          </ControlButton>
          
          <ControlButton 
            variants={itemVariants}
            iconColor="#f39c12"
            onClick={handleMemoryManagement}
            disabled={loading && activeAction === 'memory'}
          >
            {loading && activeAction === 'memory' ? (
              <LoadingSpinner />
            ) : (
              <MemoryIcon />
            )}
            <ButtonLabel>Memory Management</ButtonLabel>
            <ButtonDescription>Optimize memory allocation</ButtonDescription>
          </ControlButton>
          
          <ControlButton 
            variants={itemVariants}
            iconColor="#3498db"
            onClick={handleStorageManagement}
            disabled={loading && activeAction === 'storage'}
          >
            {loading && activeAction === 'storage' ? (
              <LoadingSpinner />
            ) : (
              <StorageIcon />
            )}
            <ButtonLabel>Storage Management</ButtonLabel>
            <ButtonDescription>Manage data storage</ButtonDescription>
          </ControlButton>
        </ControlsGrid>
        
        {results && formatResults()}
      </PanelContainer>
      
      {showCommandSheet && (
        <CommandSheetModal
          initial="hidden"
          animate="visible"
          exit="exit"
          variants={modalVariants}
        >
          <CommandSheetContent variants={modalContentVariants}>
            <CommandSheetHeader>
              <CommandSheetTitle>Command Sheet</CommandSheetTitle>
              <CloseButton onClick={() => setShowCommandSheet(false)}>×</CloseButton>
            </CommandSheetHeader>
            
            {loading && activeAction === 'commands' ? (
              <div className="flex-center" style={{ padding: '2rem' }}>
                <LoadingSpinner size={40} />
                <p style={{ marginLeft: '1rem' }}>Loading commands...</p>
              </div>
            ) : (
              <>
                <CommandSection>
                  <CommandSectionTitle>Core Commands</CommandSectionTitle>
                  <CommandTable>
                    <tbody>
                      {commandSections.core && commandSections.core.map((cmd, index) => (
                        <CommandRow key={index}>
                          <CommandCell>{cmd.command}</CommandCell>
                          <CommandCell>{cmd.description}</CommandCell>
                        </CommandRow>
                      ))}
                    </tbody>
                  </CommandTable>
                </CommandSection>
                
                <CommandSection>
                  <CommandSectionTitle>Agent Commands</CommandSectionTitle>
                  <CommandTable>
                    <tbody>
                      {commandSections.agent && commandSections.agent.map((cmd, index) => (
                        <CommandRow key={index}>
                          <CommandCell>{cmd.command}</CommandCell>
                          <CommandCell>{cmd.description}</CommandCell>
                        </CommandRow>
                      ))}
                    </tbody>
                  </CommandTable>
                </CommandSection>
                
                <CommandSection>
                  <CommandSectionTitle>Memory Commands</CommandSectionTitle>
                  <CommandTable>
                    <tbody>
                      {commandSections.memory && commandSections.memory.map((cmd, index) => (
                        <CommandRow key={index}>
                          <CommandCell>{cmd.command}</CommandCell>
                          <CommandCell>{cmd.description}</CommandCell>
                        </CommandRow>
                      ))}
                    </tbody>
                  </CommandTable>
                </CommandSection>
                
                <CommandSection>
                  <CommandSectionTitle>System Commands</CommandSectionTitle>
                  <CommandTable>
                    <tbody>
                      {commandSections.system && commandSections.system.map((cmd, index) => (
                        <CommandRow key={index}>
                          <CommandCell>{cmd.command}</CommandCell>
                          <CommandCell>{cmd.description}</CommandCell>
                        </CommandRow>
                      ))}
                    </tbody>
                  </CommandTable>
                </CommandSection>
              </>
            )}
          </CommandSheetContent>
        </CommandSheetModal>
      )}
    </>
  );
};

export default GPTControlPanel;
