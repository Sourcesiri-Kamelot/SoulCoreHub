import React, { useState, useContext, useEffect, useRef } from 'react';
import { AnimaContext } from '../contexts/AnimaContext';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';
import { systemApi } from '../services/apiService';

// Icons
import SendIcon from '@mui/icons-material/Send';
import HistoryIcon from '@mui/icons-material/History';
import CloseIcon from '@mui/icons-material/Close';
import TerminalIcon from '@mui/icons-material/Terminal';
import CircularProgress from '@mui/icons-material/CircularProgress';

const CommandContainer = styled(motion.div)`
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  max-width: 800px;
  background: rgba(10, 10, 26, 0.8);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius);
  border: 1px solid rgba(106, 17, 203, 0.3);
  padding: 1rem;
  box-shadow: var(--shadow-medium), var(--glow-soft);
  z-index: 100;
  display: flex;
  flex-direction: column;
`;

const CommandHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
`;

const CommandTitle = styled.h3`
  font-family: var(--font-display);
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary-light);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  svg {
    font-size: 1.2rem;
    color: var(--accent-1);
  }
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: var(--primary-light);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    color: var(--accent-1);
  }
  
  svg {
    font-size: 1.2rem;
  }
`;

const CommandForm = styled.form`
  display: flex;
  gap: 0.5rem;
`;

const CommandInputField = styled.input`
  flex: 1;
  background: rgba(10, 10, 26, 0.5);
  border: 1px solid rgba(106, 17, 203, 0.2);
  color: var(--primary-light);
  border-radius: var(--border-radius);
  padding: 0.75rem 1rem;
  font-family: monospace;
  font-size: 0.9rem;
  
  &:focus {
    outline: none;
    border-color: rgba(106, 17, 203, 0.5);
    box-shadow: 0 0 0 2px rgba(106, 17, 203, 0.2);
  }
  
  &::placeholder {
    color: rgba(248, 249, 250, 0.5);
  }
`;

const CommandButton = styled.button`
  background: rgba(106, 17, 203, 0.3);
  border: 1px solid rgba(106, 17, 203, 0.5);
  color: var(--primary-light);
  border-radius: var(--border-radius);
  padding: 0 1rem;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all var(--transition-speed);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: ${props => props.disabled ? 0.7 : 1};
  
  &:hover {
    background: ${props => props.disabled ? 'rgba(106, 17, 203, 0.3)' : 'rgba(106, 17, 203, 0.4)'};
    border-color: ${props => props.disabled ? 'rgba(106, 17, 203, 0.5)' : 'rgba(106, 17, 203, 0.6)'};
  }
  
  svg {
    font-size: 1.2rem;
  }
`;

const HistoryButton = styled(CommandButton)`
  background: rgba(10, 10, 26, 0.5);
  border: 1px solid rgba(106, 17, 203, 0.2);
  
  &:hover {
    background: rgba(10, 10, 26, 0.7);
    border-color: rgba(106, 17, 203, 0.4);
  }
`;

const CommandResponse = styled.div`
  margin-top: 1rem;
  background: rgba(10, 10, 26, 0.5);
  border: 1px solid rgba(106, 17, 203, 0.2);
  border-radius: var(--border-radius);
  padding: 0.75rem;
  font-family: monospace;
  font-size: 0.9rem;
  color: var(--primary-light);
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  
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

const HistorySidebar = styled(motion.div)`
  position: fixed;
  top: 0;
  right: 0;
  width: 300px;
  height: 100%;
  background: rgba(10, 10, 26, 0.9);
  backdrop-filter: blur(10px);
  border-left: 1px solid rgba(106, 17, 203, 0.3);
  padding: 1rem;
  z-index: 200;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-hard);
`;

const HistoryHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(106, 17, 203, 0.3);
`;

const HistoryTitle = styled.h3`
  font-family: var(--font-display);
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--primary-light);
`;

const HistoryList = styled.div`
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  
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

const HistoryItem = styled.div`
  background: rgba(10, 10, 26, 0.5);
  border: 1px solid rgba(106, 17, 203, 0.2);
  border-radius: var(--border-radius);
  padding: 0.75rem;
  cursor: pointer;
  transition: all var(--transition-speed);
  
  &:hover {
    background: rgba(10, 10, 26, 0.7);
    border-color: rgba(106, 17, 203, 0.4);
  }
`;

const HistoryCommand = styled.div`
  font-family: monospace;
  font-size: 0.9rem;
  color: var(--accent-1);
  margin-bottom: 0.25rem;
`;

const HistoryTimestamp = styled.div`
  font-size: 0.8rem;
  color: rgba(248, 249, 250, 0.5);
`;

const LoadingSpinner = styled(CircularProgress)`
  color: var(--accent-1);
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

const CommandInput = () => {
  const { addNotification } = useContext(AnimaContext);
  const [command, setCommand] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [commandHistory, setCommandHistory] = useState([]);
  const inputRef = useRef(null);
  
  // Load command history on mount
  useEffect(() => {
    const loadCommandHistory = async () => {
      try {
        const history = await systemApi.getCommandHistory();
        setCommandHistory(history);
      } catch (error) {
        console.error('Failed to load command history:', error);
      }
    };
    
    loadCommandHistory();
  }, []);
  
  // Focus input when component mounts
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);
  
  // Handle command submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!command.trim()) return;
    
    setLoading(true);
    setResponse('');
    
    try {
      const result = await systemApi.executeCommand(command);
      
      // Add command to history
      const newHistoryItem = {
        command,
        timestamp: new Date(),
        response: result.output
      };
      
      setCommandHistory(prev => [newHistoryItem, ...prev]);
      
      // Set response
      setResponse(result.output);
      
      // Clear command
      setCommand('');
      
      // Show notification
      if (result.status === 'success') {
        addNotification('success', 'Command Executed', `Command "${command}" executed successfully.`);
      } else {
        addNotification('warning', 'Command Warning', `Command "${command}" executed with warnings.`);
      }
    } catch (error) {
      console.error('Failed to execute command:', error);
      setResponse(`Error: ${error.message || 'Failed to execute command'}`);
      addNotification('error', 'Command Failed', `Could not execute command "${command}".`);
    } finally {
      setLoading(false);
    }
  };
  
  // Handle history item click
  const handleHistoryItemClick = (historyItem) => {
    setCommand(historyItem.command);
    setShowHistory(false);
    
    // Focus input
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };
  
  // Animation variants
  const containerVariants = {
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
  
  const sidebarVariants = {
    hidden: { x: 300 },
    visible: { 
      x: 0,
      transition: { 
        type: "spring", 
        damping: 25, 
        stiffness: 500 
      }
    },
    exit: { 
      x: 300,
      transition: { duration: 0.3 }
    }
  };
  
  return (
    <>
      <CommandContainer
        initial="hidden"
        animate="visible"
        exit="exit"
        variants={containerVariants}
      >
        <CommandHeader>
          <CommandTitle>
            <TerminalIcon />
            Command Input
          </CommandTitle>
          <CloseButton onClick={() => setShowHistory(!showHistory)}>
            <HistoryIcon />
          </CloseButton>
        </CommandHeader>
        
        <CommandForm onSubmit={handleSubmit}>
          <CommandInputField 
            ref={inputRef}
            type="text" 
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            placeholder="Enter command..."
            disabled={loading}
          />
          <CommandButton type="submit" disabled={loading || !command.trim()}>
            {loading ? <LoadingSpinner size={20} /> : <SendIcon />}
          </CommandButton>
        </CommandForm>
        
        {response && (
          <CommandResponse>
            {response}
          </CommandResponse>
        )}
      </CommandContainer>
      
      {showHistory && (
        <HistorySidebar
          initial="hidden"
          animate="visible"
          exit="exit"
          variants={sidebarVariants}
        >
          <HistoryHeader>
            <HistoryTitle>Command History</HistoryTitle>
            <CloseButton onClick={() => setShowHistory(false)}>
              <CloseIcon />
            </CloseButton>
          </HistoryHeader>
          
          <HistoryList>
            {commandHistory.length > 0 ? (
              commandHistory.map((historyItem, index) => (
                <HistoryItem 
                  key={index}
                  onClick={() => handleHistoryItemClick(historyItem)}
                >
                  <HistoryCommand>{historyItem.command}</HistoryCommand>
                  <HistoryTimestamp>{formatTimestamp(historyItem.timestamp)}</HistoryTimestamp>
                </HistoryItem>
              ))
            ) : (
              <div style={{ color: 'rgba(248, 249, 250, 0.5)', textAlign: 'center', padding: '1rem' }}>
                No command history
              </div>
            )}
          </HistoryList>
        </HistorySidebar>
      )}
    </>
  );
};

export default CommandInput;
