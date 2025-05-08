import React, { useEffect, useState } from 'react';

const EnhancedAgentTyping = ({ agentId, agent }) => {
  const [dots, setDots] = useState('...');
  
  // Animate the typing dots
  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => {
        if (prev === '...') return '.';
        if (prev === '.') return '..';
        if (prev === '..') return '...';
        return '.';
      });
    }, 500);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className={`enhanced-chat-bubble agent typing ${agentId}`}>
      <div className="bubble-header">
        <div 
          className="agent-avatar-tiny" 
          style={{ backgroundImage: `url(${agent?.avatar || '/assets/default-agent.png'})` }}
        ></div>
        <div className="agent-name">{agent?.name || agentId}</div>
      </div>
      
      <div className="bubble-content">
        <div className="typing-indicator">
          <span className="typing-dot"></span>
          <span className="typing-dot"></span>
          <span className="typing-dot"></span>
        </div>
      </div>
    </div>
  );
};

export default EnhancedAgentTyping;
