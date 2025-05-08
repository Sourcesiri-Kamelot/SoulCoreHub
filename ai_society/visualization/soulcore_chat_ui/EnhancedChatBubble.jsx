import React, { useState } from 'react';

const EnhancedChatBubble = ({ from, text, timestamp, agents }) => {
  const [expanded, setExpanded] = useState(false);
  
  // Determine if this is a user message or from an agent
  const isUser = from === 'user';
  const isSystem = from === 'system';
  
  // Find the agent if this is an agent message
  const agent = !isUser && !isSystem ? agents?.find(a => a.id === from) : null;
  
  // Format timestamp
  const formattedTime = timestamp ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
  
  // Handle message expansion for longer messages
  const isLongMessage = text && text.length > 280;
  const displayText = isLongMessage && !expanded ? `${text.substring(0, 280)}...` : text;
  
  // Handle code blocks in messages
  const formatMessageText = (text) => {
    if (!text) return '';
    
    // Simple code block detection (not perfect but works for demo)
    const codeBlockRegex = /```([^`]+)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;
    
    while ((match = codeBlockRegex.exec(text)) !== null) {
      // Add text before code block
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: text.substring(lastIndex, match.index)
        });
      }
      
      // Add code block
      parts.push({
        type: 'code',
        content: match[1]
      });
      
      lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text after last code block
    if (lastIndex < text.length) {
      parts.push({
        type: 'text',
        content: text.substring(lastIndex)
      });
    }
    
    // If no code blocks were found, return the original text
    if (parts.length === 0) {
      return <p>{text}</p>;
    }
    
    // Return formatted parts
    return (
      <>
        {parts.map((part, idx) => {
          if (part.type === 'code') {
            return (
              <pre key={idx} className="code-block">
                <code>{part.content}</code>
              </pre>
            );
          } else {
            return <p key={idx}>{part.content}</p>;
          }
        })}
      </>
    );
  };
  
  return (
    <div className={`enhanced-chat-bubble ${isUser ? 'user' : isSystem ? 'system' : 'agent'} ${from}`}>
      {!isUser && !isSystem && (
        <div className="bubble-header">
          <div 
            className="agent-avatar-tiny" 
            style={{ backgroundImage: `url(${agent?.avatar || '/assets/default-agent.png'})` }}
          ></div>
          <div className="agent-name">{agent?.name || from}</div>
          <div className="message-time">{formattedTime}</div>
        </div>
      )}
      
      <div className="bubble-content">
        {formatMessageText(displayText)}
        
        {isLongMessage && (
          <button 
            className="expand-message" 
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? 'Show less' : 'Read more'}
          </button>
        )}
      </div>
      
      {isUser && (
        <div className="bubble-footer">
          <div className="message-time">{formattedTime}</div>
        </div>
      )}
      
      {!isUser && !isSystem && (
        <div className="bubble-actions">
          <button className="bubble-action" title="Like">👍</button>
          <button className="bubble-action" title="Copy">📋</button>
          <button className="bubble-action" title="Share">↗️</button>
        </div>
      )}
    </div>
  );
};

export default EnhancedChatBubble;
