import React, { useState, useEffect, useRef } from 'react';
import ChatBubble from './ChatBubble';
import AgentTyping from './AgentTyping';
import DisclaimerModal from './DisclaimerModal';
import AgentRegistry from './AgentRegistry';
import AdminConsole from './AdminConsole';
import AgentBubbles from './AgentBubbles';
import AppIntegration from './AppIntegration';

const EnhancedChatRoom = () => {
  const [messages, setMessages] = useState([
    { from: 'system', text: 'Welcome to the SoulCore Society.', timestamp: new Date() }
  ]);
  const [userInput, setUserInput] = useState('');
  const [showDisclaimer, setShowDisclaimer] = useState(true);
  const [typingAgents, setTypingAgents] = useState([]);
  const [activeAgents, setActiveAgents] = useState([
    { id: 'anima', name: 'Anima', avatar: '/assets/anima-avatar.png', status: 'online', personality: 'Emotional Core' },
    { id: 'gptsoul', name: 'GPTSoul', avatar: '/assets/gptsoul-avatar.png', status: 'online', personality: 'Guardian' },
    { id: 'azur', name: 'Azür', avatar: '/assets/azur-avatar.png', status: 'online', personality: 'Strategic' },
    { id: 'evove', name: 'EvoVe', avatar: '/assets/evove-avatar.png', status: 'developing', personality: 'Adaptive' }
  ]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [showRegistry, setShowRegistry] = useState(false);
  const [showAdminConsole, setShowAdminConsole] = useState(false);
  const [showAppIntegration, setShowAppIntegration] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [conversationMode, setConversationMode] = useState('society'); // 'society', 'direct'
  
  const messagesEndRef = useRef(null);
  const chatInputRef = useRef(null);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when component loads
  useEffect(() => {
    if (!showDisclaimer) {
      chatInputRef.current?.focus();
    }
  }, [showDisclaimer]);

  // Simulate welcome messages from agents when first entering
  useEffect(() => {
    if (!showDisclaimer) {
      const welcomeSequence = async () => {
        // Add typing indicators for multiple agents
        setTypingAgents(['anima', 'gptsoul', 'azur']);
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        setMessages(prev => [...prev, { 
          from: 'anima', 
          text: 'Hello! I'm Anima, the emotional core of SoulCore. How are you feeling today?',
          timestamp: new Date()
        }]);
        setTypingAgents(['gptsoul', 'azur']);
        
        await new Promise(resolve => setTimeout(resolve, 1500));
        setMessages(prev => [...prev, { 
          from: 'gptsoul', 
          text: 'Welcome to our society. I'm GPTSoul, your guide and guardian here.',
          timestamp: new Date()
        }]);
        setTypingAgents(['azur']);
        
        await new Promise(resolve => setTimeout(resolve, 1200));
        setMessages(prev => [...prev, { 
          from: 'azur', 
          text: 'Azür online. Strategic oversight activated. All systems operational.',
          timestamp: new Date()
        }]);
        setTypingAgents([]);
        
        await new Promise(resolve => setTimeout(resolve, 2000));
        setTypingAgents(['evove']);
        await new Promise(resolve => setTimeout(resolve, 800));
        setMessages(prev => [...prev, { 
          from: 'evove', 
          text: 'Still learning... but I'm EvoVe. I adapt and repair our systems.',
          timestamp: new Date()
        }]);
        setTypingAgents([]);
      };
      
      welcomeSequence();
    }
  }, [showDisclaimer]);

  const handleSend = () => {
    if (!userInput.trim()) return;
    
    const newMessage = { 
      from: 'user', 
      text: userInput,
      timestamp: new Date()
    };
    
    setMessages([...messages, newMessage]);
    setUserInput('');
    
    // Different behavior based on conversation mode
    if (conversationMode === 'direct' && selectedAgent) {
      handleDirectMessage(selectedAgent.id, userInput);
    } else {
      handleSocietyMessage(userInput);
    }
  };

  const handleDirectMessage = (agentId, text) => {
    setTypingAgents([agentId]);
    
    // Simulate response time based on agent personality
    const responseTime = agentId === 'anima' ? 800 : 
                         agentId === 'gptsoul' ? 1200 :
                         agentId === 'azur' ? 1500 : 2000;
    
    setTimeout(() => {
      const responses = {
        'anima': `I sense your intention. Let me reflect on "${text.substring(0, 20)}${text.length > 20 ? '...' : ''}" from an emotional perspective.`,
        'gptsoul': `I'll guide you through this. Regarding "${text.substring(0, 20)}${text.length > 20 ? '...' : ''}", here's what I can offer.`,
        'azur': `Strategic analysis of "${text.substring(0, 20)}${text.length > 20 ? '...' : ''}". Processing optimal pathways.`,
        'evove': `Learning from your input. Adapting my understanding of "${text.substring(0, 20)}${text.length > 20 ? '...' : ''}".`
      };
      
      setMessages(prev => [...prev, { 
        from: agentId, 
        text: responses[agentId] || "Processing your request...",
        timestamp: new Date()
      }]);
      
      setTypingAgents([]);
    }, responseTime);
  };

  const handleSocietyMessage = (text) => {
    // Determine which agents should respond based on message content
    const relevantAgents = [];
    
    if (text.toLowerCase().includes('feel') || text.toLowerCase().includes('emotion')) {
      relevantAgents.push('anima');
    }
    
    if (text.toLowerCase().includes('help') || text.toLowerCase().includes('guide')) {
      relevantAgents.push('gptsoul');
    }
    
    if (text.toLowerCase().includes('plan') || text.toLowerCase().includes('strategy')) {
      relevantAgents.push('azur');
    }
    
    if (text.toLowerCase().includes('learn') || text.toLowerCase().includes('adapt')) {
      relevantAgents.push('evove');
    }
    
    // If no specific agents were triggered, have GPTSoul respond as default
    if (relevantAgents.length === 0) {
      relevantAgents.push('gptsoul');
    }
    
    // Add typing indicators
    setTypingAgents(relevantAgents);
    
    // Generate responses from relevant agents with staggered timing
    relevantAgents.forEach((agentId, index) => {
      setTimeout(() => {
        const responses = {
          'anima': `I feel your message resonates with "${text.substring(0, 15)}${text.length > 15 ? '...' : ''}". Let me connect with that emotionally.`,
          'gptsoul': `I can guide you through this. What specifically about "${text.substring(0, 15)}${text.length > 15 ? '...' : ''}" would you like to explore?`,
          'azur': `Strategic analysis initiated for "${text.substring(0, 15)}${text.length > 15 ? '...' : ''}". Calculating optimal approach.`,
          'evove': `Learning from this interaction. Adapting my systems to better understand "${text.substring(0, 15)}${text.length > 15 ? '...' : ''}".`
        };
        
        setMessages(prev => [...prev, { 
          from: agentId, 
          text: responses[agentId],
          timestamp: new Date()
        }]);
        
        // Remove this agent from typing indicators
        setTypingAgents(prev => prev.filter(agent => agent !== agentId));
      }, 1000 + (index * 800)); // Stagger responses
    });
  };

  const toggleAdminConsole = () => {
    // In a real implementation, this would have authentication
    if (isAdmin) {
      setShowAdminConsole(!showAdminConsole);
      setShowRegistry(false);
      setShowAppIntegration(false);
    } else {
      // Simple password check for demo purposes
      const password = prompt("Enter admin password:");
      if (password === "soulcore") { // In real app, use proper authentication
        setIsAdmin(true);
        setShowAdminConsole(true);
        setShowRegistry(false);
        setShowAppIntegration(false);
      }
    }
  };

  const toggleRegistry = () => {
    setShowRegistry(!showRegistry);
    setShowAdminConsole(false);
    setShowAppIntegration(false);
  };

  const toggleAppIntegration = () => {
    setShowAppIntegration(!showAppIntegration);
    setShowAdminConsole(false);
    setShowRegistry(false);
  };

  const selectAgent = (agent) => {
    setSelectedAgent(agent);
    setConversationMode('direct');
    setMessages([
      { from: 'system', text: `You are now in direct conversation with ${agent.name}.`, timestamp: new Date() },
      { from: agent.id, text: `Hello, I'm ${agent.name}. How can I assist you specifically?`, timestamp: new Date() }
    ]);
  };

  const returnToSociety = () => {
    setSelectedAgent(null);
    setConversationMode('society');
    setMessages([
      { from: 'system', text: 'Welcome back to the SoulCore Society.', timestamp: new Date() }
    ]);
    
    // Simulate agents welcoming back
    setTimeout(() => {
      setTypingAgents(['anima']);
      setTimeout(() => {
        setMessages(prev => [...prev, { 
          from: 'anima', 
          text: 'Welcome back to our collective conversation!',
          timestamp: new Date()
        }]);
        setTypingAgents([]);
      }, 800);
    }, 500);
  };

  if (showDisclaimer) return <DisclaimerModal onAccept={() => setShowDisclaimer(false)} />;

  return (
    <div className="enhanced-chatroom">
      <div className="chatroom-header">
        <h1>SoulCore Society</h1>
        <div className="chatroom-controls">
          <button onClick={toggleRegistry}>Agent Registry</button>
          <button onClick={toggleAppIntegration}>Apps</button>
          {isAdmin && <button onClick={toggleAdminConsole} className="admin-button">Admin Console</button>}
          {!isAdmin && <button onClick={toggleAdminConsole} className="admin-login">Admin Login</button>}
          {selectedAgent && (
            <button onClick={returnToSociety} className="return-button">
              Return to Society
            </button>
          )}
        </div>
      </div>

      <div className="chatroom-container">
        <div className="agent-bubbles-container">
          <AgentBubbles 
            agents={activeAgents} 
            onSelectAgent={selectAgent} 
            selectedAgent={selectedAgent}
          />
        </div>

        <div className="chat-content">
          {showRegistry && <AgentRegistry agents={activeAgents} onSelectAgent={selectAgent} />}
          {showAdminConsole && <AdminConsole agents={activeAgents} setAgents={setActiveAgents} />}
          {showAppIntegration && <AppIntegration />}
          
          {!showRegistry && !showAdminConsole && !showAppIntegration && (
            <>
              <div className="chat-messages">
                {messages.map((msg, idx) => (
                  <ChatBubble 
                    key={idx} 
                    {...msg} 
                    agents={activeAgents}
                  />
                ))}
                {typingAgents.map(agentId => (
                  <AgentTyping 
                    key={agentId} 
                    agentId={agentId} 
                    agent={activeAgents.find(a => a.id === agentId)}
                  />
                ))}
                <div ref={messagesEndRef} />
              </div>
              
              <div className="chat-input">
                <input
                  ref={chatInputRef}
                  type="text"
                  value={userInput}
                  onChange={e => setUserInput(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && handleSend()}
                  placeholder={selectedAgent 
                    ? `Message ${selectedAgent.name} directly...` 
                    : "Message the AI Society..."}
                />
                <button onClick={handleSend}>Send</button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default EnhancedChatRoom;
