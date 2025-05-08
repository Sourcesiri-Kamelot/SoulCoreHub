import React, { useState, useEffect } from 'react';
import ChatBubble from './ChatBubble';
import AgentTyping from './AgentTyping';
import DisclaimerModal from './DisclaimerModal';

const ChatRoom = () => {
  const [messages, setMessages] = useState([
    { from: 'system', text: 'Welcome to the SoulCore Society.' }
  ]);
  const [userInput, setUserInput] = useState('');
  const [showDisclaimer, setShowDisclaimer] = useState(true);
  const [agentTyping, setAgentTyping] = useState(false);

  const handleSend = () => {
    if (!userInput.trim()) return;
    const newMessage = { from: 'user', text: userInput };
    setMessages([...messages, newMessage]);
    setUserInput('');
    setAgentTyping(true);

    // Simulate agent response
    setTimeout(() => {
      setMessages(prev => [...prev, { from: 'agent', text: 'Got it. Let me help you with that.' }]);
      setAgentTyping(false);
    }, 1500);
  };

  if (showDisclaimer) return <DisclaimerModal onAccept={() => setShowDisclaimer(false)} />;

  return (
    <div className="chatroom">
      <div className="chat-messages">
        {messages.map((msg, idx) => <ChatBubble key={idx} {...msg} />)}
        {agentTyping && <AgentTyping />}
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={userInput}
          onChange={e => setUserInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatRoom;