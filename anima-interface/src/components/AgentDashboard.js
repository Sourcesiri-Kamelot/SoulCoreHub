import React, { useContext, useState, useEffect } from 'react';
import { AnimaContext } from '../contexts/AnimaContext';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';
import { agentApi } from '../services/apiService';
import websocketService from '../services/websocketService';

// Icons
import DiamondIcon from '@mui/icons-material/Diamond';
import FavoriteIcon from '@mui/icons-material/Favorite';
import RefreshIcon from '@mui/icons-material/Refresh';
import CloudIcon from '@mui/icons-material/Cloud';
import CodeIcon from '@mui/icons-material/Code';
import SearchIcon from '@mui/icons-material/Search';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import InfoIcon from '@mui/icons-material/Info';
import SettingsIcon from '@mui/icons-material/Settings';
import NetworkPingIcon from '@mui/icons-material/NetworkPing';
import CircularProgress from '@mui/icons-material/CircularProgress';

const DashboardContainer = styled(motion.div)`
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

const DashboardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(106, 17, 203, 0.3);
`;

const DashboardTitle = styled.h2`
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

const FilterContainer = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
`;

const FilterButton = styled.button`
  background: ${props => props.active ? 'rgba(106, 17, 203, 0.3)' : 'rgba(10, 10, 26, 0.5)'};
  border: 1px solid ${props => props.active ? 'rgba(106, 17, 203, 0.5)' : 'rgba(106, 17, 203, 0.2)'};
  color: var(--primary-light);
  border-radius: var(--border-radius);
  padding: 0.25rem 0.75rem;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all var(--transition-speed);
  
  &:hover {
    background: rgba(106, 17, 203, 0.2);
    border-color: rgba(106, 17, 203, 0.4);
  }
`;

const AgentsContainer = styled.div`
  overflow-y: auto;
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  padding-right: 0.5rem;
  
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

const AgentCard = styled(motion.div)`
  background: rgba(10, 10, 26, 0.5);
  border-radius: var(--border-radius);
  border: 1px solid rgba(106, 17, 203, 0.2);
  padding: 1rem;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  
  &:hover {
    border-color: rgba(106, 17, 203, 0.4);
    box-shadow: 0 0 15px rgba(106, 17, 203, 0.2);
  }
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: ${props => props.color || 'var(--accent-1)'};
  }
`;

const AgentHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
`;

const AgentAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: ${props => props.color || 'var(--accent-1)'};
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.75rem;
  box-shadow: 0 0 10px ${props => props.color || 'var(--accent-1)'};
  
  svg {
    color: white;
    font-size: 1.25rem;
  }
`;

const AgentInfo = styled.div`
  flex: 1;
`;

const AgentName = styled.h3`
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--primary-light);
`;

const AgentType = styled.div`
  font-size: 0.8rem;
  color: rgba(248, 249, 250, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const AgentStatus = styled.div`
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: ${props => props.active ? '#2ecc71' : '#e74c3c'};
  box-shadow: 0 0 5px ${props => props.active ? '#2ecc71' : '#e74c3c'};
`;

const AgentDescription = styled.p`
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
  color: rgba(248, 249, 250, 0.9);
`;

const AgentCapabilities = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
`;

const AgentCapability = styled.span`
  background: rgba(10, 10, 26, 0.7);
  border: 1px solid rgba(106, 17, 203, 0.2);
  border-radius: 12px;
  padding: 0.1rem 0.5rem;
  font-size: 0.7rem;
  color: rgba(248, 249, 250, 0.8);
`;

const AgentActions = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: auto;
`;

const ActionButton = styled.button`
  background: rgba(10, 10, 26, 0.7);
  border: 1px solid rgba(106, 17, 203, 0.2);
  color: var(--primary-light);
  border-radius: var(--border-radius);
  padding: 0.5rem;
  font-size: 0.9rem;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all var(--transition-speed);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: ${props => props.disabled ? 0.5 : 1};
  
  &:hover {
    background: ${props => props.disabled ? 'rgba(10, 10, 26, 0.7)' : 'rgba(106, 17, 203, 0.2)'};
    border-color: ${props => props.disabled ? 'rgba(106, 17, 203, 0.2)' : 'rgba(106, 17, 203, 0.4)'};
  }
  
  svg {
    font-size: 1.2rem;
  }
`;

const PrimaryActionButton = styled(ActionButton)`
  background: ${props => props.active ? 'rgba(231, 76, 60, 0.3)' : 'rgba(46, 204, 113, 0.3)'};
  border-color: ${props => props.active ? 'rgba(231, 76, 60, 0.5)' : 'rgba(46, 204, 113, 0.5)'};
  padding: 0.5rem 1rem;
  flex: 1;
  margin-right: 0.5rem;
  
  &:hover {
    background: ${props => props.disabled ? (props.active ? 'rgba(231, 76, 60, 0.3)' : 'rgba(46, 204, 113, 0.3)') : (props.active ? 'rgba(231, 76, 60, 0.4)' : 'rgba(46, 204, 113, 0.4)')};
    border-color: ${props => props.disabled ? (props.active ? 'rgba(231, 76, 60, 0.5)' : 'rgba(46, 204, 113, 0.5)') : (props.active ? 'rgba(231, 76, 60, 0.6)' : 'rgba(46, 204, 113, 0.6)')};
  }
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(248, 249, 250, 0.5);
  text-align: center;
  padding: 2rem;
  grid-column: 1 / -1;
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  grid-column: 1 / -1;
`;

const LoadingSpinner = styled(CircularProgress)`
  color: var(--accent-1);
  margin-bottom: 1rem;
`;

const LoadingText = styled.div`
  color: var(--primary-light);
  font-size: 1.2rem;
`;

// Helper function to get avatar icon based on agent type
const getAgentAvatar = (avatarType) => {
  switch (avatarType) {
    case 'diamond':
      return <DiamondIcon />;
    case 'heart':
      return <FavoriteIcon />;
    case 'refresh':
      return <RefreshIcon />;
    case 'cloud':
      return <CloudIcon />;
    case 'code':
      return <CodeIcon />;
    case 'search':
      return <SearchIcon />;
    default:
      return <DiamondIcon />;
  }
};

const AgentDashboard = () => {
  const { addNotification } = useContext(AnimaContext);
  const [activeFilter, setActiveFilter] = useState('all');
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [actionInProgress, setActionInProgress] = useState(null);
  
  // Load agents on component mount
  useEffect(() => {
    const loadAgents = async () => {
      setLoading(true);
      try {
        const agentList = await agentApi.getStatus();
        setAgents(agentList);
      } catch (error) {
        console.error('Failed to load agents:', error);
        addNotification('error', 'Agent Loading Failed', 'Could not load agent status.');
      } finally {
        setLoading(false);
      }
    };
    
    loadAgents();
    
    // Set up WebSocket listener for agent updates
    websocketService.connect().catch(error => {
      console.error('Failed to connect to WebSocket:', error);
    });
    
    const handleAgentUpdate = (data) => {
      // Update specific agent status
      if (data.agentId) {
        setAgents(prev => prev.map(agent => 
          agent.id === data.agentId ? { ...agent, ...data } : agent
        ));
        
        // Show notification for status changes
        if (data.status === 'active') {
          addNotification('success', 'Agent Activated', `Agent ${data.name || data.agentId} is now active.`);
        } else if (data.status === 'inactive') {
          addNotification('info', 'Agent Deactivated', `Agent ${data.name || data.agentId} is now inactive.`);
        }
      } else {
        // Reload all agents if no specific agent ID
        loadAgents();
      }
    };
    
    websocketService.on('agent_update', handleAgentUpdate);
    
    // Clean up listener when component unmounts
    return () => {
      websocketService.off('agent_update', handleAgentUpdate);
    };
  }, [addNotification]);
  
  // Filter agents based on active filter
  const filteredAgents = activeFilter === 'all' 
    ? agents 
    : agents.filter(agent => agent.type === activeFilter);
    
  // Handle deploy/stop agent
  const handleAgentAction = async (agentId, isActive) => {
    setActionInProgress(agentId);
    
    try {
      if (!isActive) {
        // Deploy agent
        await agentApi.deploy(agentId);
        addNotification('success', 'Agent Deployed', `Agent ${agentId} has been deployed.`);
      } else {
        // Stop agent
        await agentApi.reboot(agentId);
        addNotification('info', 'Agent Rebooted', `Agent ${agentId} has been rebooted.`);
      }
    } catch (error) {
      console.error(`Failed to ${isActive ? 'reboot' : 'deploy'} agent:`, error);
      addNotification('error', `${isActive ? 'Reboot' : 'Deployment'} Failed`, 
        `Could not ${isActive ? 'reboot' : 'deploy'} agent ${agentId}.`);
    } finally {
      setActionInProgress(null);
    }
  };
  
  // Handle ping agent
  const handlePingAgent = async (agentId) => {
    setActionInProgress(`ping-${agentId}`);
    
    try {
      const result = await agentApi.ping(agentId);
      
      if (result.status === 'ok') {
        addNotification('success', 'Agent Ping', `Agent ${agentId} responded in ${result.latency}ms.`);
      } else {
        addNotification('warning', 'Agent Ping', `Agent ${agentId} response: ${result.status}`);
      }
    } catch (error) {
      console.error('Failed to ping agent:', error);
      addNotification('error', 'Ping Failed', `Could not ping agent ${agentId}.`);
    } finally {
      setActionInProgress(null);
    }
  };
  
  // Handle view agent details
  const handleViewAgentDetails = async (agentId) => {
    setActionInProgress(`info-${agentId}`);
    
    try {
      const details = await agentApi.getDetails(agentId);
      
      // Format details for notification
      const detailsText = `
Type: ${details.type}
Status: ${details.status}
Version: ${details.version}
Uptime: ${details.uptime}
Memory Usage: ${details.memoryUsage}MB
      `;
      
      addNotification('info', `Agent ${details.name} Details`, detailsText);
    } catch (error) {
      console.error('Failed to get agent details:', error);
      addNotification('error', 'Details Failed', `Could not get details for agent ${agentId}.`);
    } finally {
      setActionInProgress(null);
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
  
  return (
    <DashboardContainer
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      <DashboardHeader>
        <DashboardTitle>Agent Dashboard</DashboardTitle>
        <span>{filteredAgents.length} agents</span>
      </DashboardHeader>
      
      <FilterContainer>
        <FilterButton 
          active={activeFilter === 'all'} 
          onClick={() => setActiveFilter('all')}
        >
          All
        </FilterButton>
        <FilterButton 
          active={activeFilter === 'core'} 
          onClick={() => setActiveFilter('core')}
        >
          Core
        </FilterButton>
        <FilterButton 
          active={activeFilter === 'utility'} 
          onClick={() => setActiveFilter('utility')}
        >
          Utility
        </FilterButton>
      </FilterContainer>
      
      <AgentsContainer>
        {loading ? (
          <LoadingContainer>
            <LoadingSpinner />
            <LoadingText>Loading agents...</LoadingText>
          </LoadingContainer>
        ) : filteredAgents.length > 0 ? (
          filteredAgents.map((agent) => (
            <AgentCard 
              key={agent.id}
              color={agent.color}
              variants={itemVariants}
            >
              <AgentStatus active={agent.status === 'active'} />
              
              <AgentHeader>
                <AgentAvatar color={agent.color}>
                  {getAgentAvatar(agent.avatar)}
                </AgentAvatar>
                <AgentInfo>
                  <AgentName>{agent.name}</AgentName>
                  <AgentType>{agent.type}</AgentType>
                </AgentInfo>
              </AgentHeader>
              
              <AgentDescription>{agent.description}</AgentDescription>
              
              <AgentCapabilities>
                {agent.capabilities.map((capability, index) => (
                  <AgentCapability key={index}>{capability}</AgentCapability>
                ))}
              </AgentCapabilities>
              
              <AgentActions>
                <PrimaryActionButton 
                  active={agent.status === 'active'}
                  onClick={() => handleAgentAction(agent.id, agent.status === 'active')}
                  disabled={actionInProgress === agent.id}
                >
                  {actionInProgress === agent.id ? (
                    <LoadingSpinner size={20} />
                  ) : agent.status === 'active' ? (
                    <>
                      <RefreshIcon style={{ marginRight: '0.5rem' }} />
                      Reboot
                    </>
                  ) : (
                    <>
                      <PlayArrowIcon style={{ marginRight: '0.5rem' }} />
                      Deploy
                    </>
                  )}
                </PrimaryActionButton>
                
                <ActionButton 
                  onClick={() => handlePingAgent(agent.id)}
                  disabled={actionInProgress === `ping-${agent.id}`}
                >
                  {actionInProgress === `ping-${agent.id}` ? (
                    <LoadingSpinner size={16} />
                  ) : (
                    <NetworkPingIcon />
                  )}
                </ActionButton>
                
                <ActionButton 
                  onClick={() => handleViewAgentDetails(agent.id)}
                  disabled={actionInProgress === `info-${agent.id}`}
                >
                  {actionInProgress === `info-${agent.id}` ? (
                    <LoadingSpinner size={16} />
                  ) : (
                    <InfoIcon />
                  )}
                </ActionButton>
              </AgentActions>
            </AgentCard>
          ))
        ) : (
          <EmptyState>
            <p>No agents found</p>
            <p>Try changing your filter</p>
          </EmptyState>
        )}
      </AgentsContainer>
    </DashboardContainer>
  );
};

export default AgentDashboard;
