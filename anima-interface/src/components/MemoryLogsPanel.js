import React, { useContext, useState, useEffect } from 'react';
import { AnimaContext } from '../contexts/AnimaContext';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';
import { memoryApi } from '../services/apiService';
import websocketService from '../services/websocketService';

// Continue with the rest of the file...

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

const SearchInput = styled.input`
  background: rgba(10, 10, 26, 0.5);
  border: 1px solid rgba(106, 17, 203, 0.2);
  color: var(--primary-light);
  border-radius: var(--border-radius);
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  width: 100%;
  margin-bottom: 1rem;
  
  &:focus {
    outline: none;
    border-color: rgba(106, 17, 203, 0.5);
    box-shadow: 0 0 0 2px rgba(106, 17, 203, 0.2);
  }
`;

const LogsContainer = styled.div`
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
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

const LogEntry = styled(motion.div)`
  background: rgba(10, 10, 26, 0.5);
  border-radius: var(--border-radius);
  border-left: 3px solid ${props => getEmotionColor(props.emotionalState)};
  padding: 0.75rem 1rem;
  position: relative;
  overflow: hidden;
  
  &:hover {
    background: rgba(10, 10, 26, 0.7);
  }
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, ${props => getEmotionColor(props.emotionalState) + '20'}, transparent);
    opacity: 0.1;
    pointer-events: none;
  }
`;

const LogHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
  color: rgba(248, 249, 250, 0.7);
`;

const LogType = styled.span`
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: ${props => getEmotionColor(props.emotionalState)};
`;

const LogTimestamp = styled.span`
  font-family: monospace;
`;

const LogContent = styled.p`
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
`;

const LogTags = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
`;

const LogTag = styled.span`
  background: rgba(10, 10, 26, 0.7);
  border: 1px solid rgba(106, 17, 203, 0.2);
  border-radius: 12px;
  padding: 0.1rem 0.5rem;
  font-size: 0.7rem;
  color: rgba(248, 249, 250, 0.8);
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
`;

// Helper function to get color based on emotional state
function getEmotionColor(state) {
  const emotionColors = {
    neutral: '#7f8c8d',
    joyful: '#f1c40f',
    focused: '#3498db',
    divine: '#9b59b6',
    furious: '#e74c3c',
    creative: '#2ecc71',
    analytical: '#1abc9c',
    transcendent: '#6a11cb',
    curious: '#f39c12'
  };
  
  return emotionColors[state] || '#7f8c8d';
}

// Format date for display
function formatDate(date) {
  return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

const MemoryLogsPanel = () => {
  const { memoryLogs } = useContext(AnimaContext);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Filter logs when filter or search changes
  useEffect(() => {
    const fetchAndFilterLogs = async () => {
      try {
        // Fetch logs from API with filters
        const filters = {
          type: activeFilter !== 'all' ? activeFilter : undefined,
          search: searchQuery || undefined,
          limit: 50
        };
        
        const logs = await memoryApi.getLogs(filters);
        setFilteredLogs(logs);
      } catch (error) {
        console.error('Failed to fetch memory logs:', error);
        setFilteredLogs([]);
      }
    };
    
    fetchAndFilterLogs();
  }, [activeFilter, searchQuery]);
  
  // Set up WebSocket listener for real-time updates
  useEffect(() => {
    // Connect to WebSocket if not already connected
    websocketService.connect().catch(error => {
      console.error('Failed to connect to WebSocket:', error);
    });
    
    // Listen for memory updates
    const handleMemoryUpdate = (data) => {
      // Fetch latest logs when memory is updated
      memoryApi.getLogs({
        type: activeFilter !== 'all' ? activeFilter : undefined,
        search: searchQuery || undefined,
        limit: 50
      }).then(logs => {
        setFilteredLogs(logs);
      }).catch(error => {
        console.error('Failed to fetch memory logs after update:', error);
      });
    };
    
    websocketService.on('memory_update', handleMemoryUpdate);
    
    // Clean up listener when component unmounts
    return () => {
      websocketService.off('memory_update', handleMemoryUpdate);
    };
  }, [activeFilter, searchQuery]);
  
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
    <PanelContainer
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      <PanelHeader>
        <PanelTitle>Memory Logs</PanelTitle>
        <span>{filteredLogs.length} entries</span>
      </PanelHeader>
      
      <FilterContainer>
        <FilterButton 
          active={activeFilter === 'all'} 
          onClick={() => setActiveFilter('all')}
        >
          All
        </FilterButton>
        <FilterButton 
          active={activeFilter === 'thought'} 
          onClick={() => setActiveFilter('thought')}
        >
          Thoughts
        </FilterButton>
        <FilterButton 
          active={activeFilter === 'decision'} 
          onClick={() => setActiveFilter('decision')}
        >
          Decisions
        </FilterButton>
        <FilterButton 
          active={activeFilter === 'reflection'} 
          onClick={() => setActiveFilter('reflection')}
        >
          Reflections
        </FilterButton>
        <FilterButton 
          active={activeFilter === 'sync'} 
          onClick={() => setActiveFilter('sync')}
        >
          Sync
        </FilterButton>
      </FilterContainer>
      
      <SearchInput 
        type="text" 
        placeholder="Search memory logs..." 
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      
      <LogsContainer>
        {filteredLogs.length > 0 ? (
          filteredLogs.map((log) => (
            <LogEntry 
              key={log.id}
              emotionalState={log.emotionalState}
              variants={itemVariants}
            >
              <LogHeader>
                <LogType emotionalState={log.emotionalState}>{log.type}</LogType>
                <LogTimestamp>{formatDate(log.timestamp)}</LogTimestamp>
              </LogHeader>
              <LogContent>{log.content}</LogContent>
              <LogTags>
                {log.tags.map((tag, index) => (
                  <LogTag key={index}>#{tag}</LogTag>
                ))}
              </LogTags>
            </LogEntry>
          ))
        ) : (
          <EmptyState>
            <p>No memory logs found</p>
            <p>Try changing your filters or search query</p>
          </EmptyState>
        )}
      </LogsContainer>
    </PanelContainer>
  );
};

export default MemoryLogsPanel;
