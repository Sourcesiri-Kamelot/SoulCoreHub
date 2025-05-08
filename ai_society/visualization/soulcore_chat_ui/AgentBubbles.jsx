import React, { useState, useEffect } from 'react';

const AgentBubbles = ({ agents, onSelectAgent, selectedAgent }) => {
  const [animatedAgents, setAnimatedAgents] = useState([]);
  
  // Create animated positions for agent bubbles
  useEffect(() => {
    // Initialize with random positions
    const initialPositions = agents.map(agent => ({
      ...agent,
      x: Math.random() * 80 + 10, // 10-90% of container width
      y: Math.random() * 80 + 10, // 10-90% of container height
      velocityX: (Math.random() - 0.5) * 0.5,
      velocityY: (Math.random() - 0.5) * 0.5,
      scale: 1,
      pulseDirection: 1,
      pulseSpeed: Math.random() * 0.01 + 0.005
    }));
    
    setAnimatedAgents(initialPositions);
    
    // Animation loop for floating effect
    const animationInterval = setInterval(() => {
      setAnimatedAgents(prevAgents => {
        return prevAgents.map(agent => {
          // Update position
          let newX = agent.x + agent.velocityX;
          let newY = agent.y + agent.velocityY;
          
          // Bounce off edges
          let newVelocityX = agent.velocityX;
          let newVelocityY = agent.velocityY;
          
          if (newX < 5 || newX > 95) {
            newVelocityX = -agent.velocityX;
            newX = newX < 5 ? 5 : 95;
          }
          
          if (newY < 5 || newY > 95) {
            newVelocityY = -agent.velocityY;
            newY = newY < 5 ? 5 : 95;
          }
          
          // Pulsing effect
          let newScale = agent.scale + (agent.pulseDirection * agent.pulseSpeed);
          let newPulseDirection = agent.pulseDirection;
          
          if (newScale > 1.1) {
            newScale = 1.1;
            newPulseDirection = -1;
          } else if (newScale < 0.9) {
            newScale = 0.9;
            newPulseDirection = 1;
          }
          
          return {
            ...agent,
            x: newX,
            y: newY,
            velocityX: newVelocityX,
            velocityY: newVelocityY,
            scale: newScale,
            pulseDirection: newPulseDirection
          };
        });
      });
    }, 50);
    
    return () => clearInterval(animationInterval);
  }, [agents]);

  return (
    <div className="agent-bubbles">
      {animatedAgents.map(agent => (
        <div
          key={agent.id}
          className={`agent-bubble ${agent.status} ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
          style={{
            left: `${agent.x}%`,
            top: `${agent.y}%`,
            transform: `scale(${agent.scale})`,
            backgroundImage: `url(${agent.avatar || '/assets/default-agent.png'})`,
          }}
          onClick={() => onSelectAgent(agent)}
        >
          <div className="agent-bubble-name">{agent.name}</div>
          <div className="agent-bubble-status"></div>
        </div>
      ))}
    </div>
  );
};

export default AgentBubbles;
